"""
Quantizer class and functions.
"""
import os
import csv
from time import time
import tempfile
import subprocess as sp
from shutil import copyfile
import numpy as np
import pandas as pd
from datasmash.config import BIN_PATH
from datasmash.utils import genesess_libfile, wait_for_file, xgenesess, pprint_dict


def vectorize_label(X, y):
    """

    """
    label_vec = []
    for lib_file, label in zip(X, y):
        lib_io = open(lib_file)
        num_lines = sum(1 for line in lib_io)
        label_vec.append([label] * num_lines)
        lib_io.close()
    label_vec = np.hstack(label_vec)
    return label_vec


def mkqdir(X, *, parent_dir, labels=None):
    """

    """
    tmp_dir = tempfile.mkdtemp(dir=parent_dir)
    if labels is None:
        copyfile(X, os.path.join(tmp_dir, os.path.basename(X)))
    else:
        library_list = []
        for lib_file, label in zip(X, labels):
            num_lines = sum(1 for line in open(lib_file))
            lib_file_name = os.path.basename(lib_file)
            library_list_line = [lib_file_name, label, num_lines]
            library_list.append(library_list_line)

            copyfile(lib_file, os.path.join(tmp_dir, lib_file_name))

        with open(os.path.join(tmp_dir, 'library_list'), 'w+') as csvfile:
            ll_writer = csv.writer(csvfile, delimiter=' ')
            for line in library_list:
                ll_writer.writerow(line)

    return tmp_dir


def fit_one_channel(directory, *, problem_type, output_type='filename', **kwargs):
    """

    """
    qtz = Quantizer(problem_type=problem_type, **kwargs)
    X = qtz.fit_transform(directory, output_type=output_type)
    return X, qtz


class Quantizer(object):
    """

    """
    def __init__(self, *,
                 problem_type,
                 num_streams=-1,
                 core_hours=28,
                 sample_size=.1,
                 bin_path=BIN_PATH,
                 pooled=True,
                 epsilon=-1,
                 min_alphabet_size=2,
                 max_alphabet_size=3,
                 gsmash=False,
                 gen_epsilon=0.02,
                 num_steps=20000,
                 num_models=1,
                 partition=None,
                 detrending=None,
                 normalization=None,
                 multi_partition=False,
                 featurization=None,
                 featurization_params=None,
                 xgenesess_hours=None,
                 verbose=False):
        self._problem_type = problem_type
        self._num_streams = num_streams
        self._core_hours = core_hours
        self._sample_size = sample_size
        self._bin_path = bin_path
        self._pooled = pooled
        self._epsilon = epsilon
        self._min_alphabet_size = min_alphabet_size
        self._max_alphabet_size = max_alphabet_size
        self._gsmash = gsmash
        self._gen_epsilon = gen_epsilon
        self._num_steps = num_steps
        self._num_models = num_models
        self._partition = partition
        self._detrending = detrending
        self._normalization = normalization
        self._featurization = featurization
        self._featurization_params = featurization_params
        self._multi_partition = multi_partition
        self._verbose = verbose
        self._command_list = []
        self._fitted = False
        self._feature_order = []

        self.quantized_data_dir = ''
        self.parameters = {}
        self.data = []
        self._partition_success_set = set()
        self.training_X = None
        self.parameter_index_map = {}

    def fit(self, data_dir):
        """
        gsmash=True only for GSmashClassification() and
        CGSmashClassification()
        """
        self.quantized_data_dir = tempfile.mkdtemp(prefix='quantized_data_',
                                                   dir=data_dir)

        if self._core_hours is not None:
            recommended_sample_size = self._get_sample_size(data_dir)
            if recommended_sample_size > 1:
                recommended_sample_size = 1
            elif recommended_sample_size <= 0:
                print('WARNING: dataset might be too large for core-hours'
                      + ' constraint.')
                recommended_sample_size = 0.1
            self._sample_size = recommended_sample_size
            self._sample_size = 0.1  #TODO: test
            print('ALLOTTED CORE-HOURS FOR QUANTIZER: {}'.format(self._core_hours))
            print('CORRESPONDING RECOMMENDED QUANTIZER SAMPLE SIZE: {}'.format(recommended_sample_size))

        self._get_command_list(data_dir)
        raw_output = sp.check_output(self._command_list, encoding='utf-8')

        #if self._problem_type == 'supervised':
        self._note_lib_files(data_dir)
        #else:
        #    self.data['dataset'] = {}
        #    self.data['dataset']['files'] = {}

        prune_range_list = []
        detrending_list = []
        normalization_list = []
        partition_list = []

        valid_params_path = os.path.join(data_dir, 'valid_parameter')
        parameters = open(valid_params_path).read().splitlines()
        #if not self._multi_partition:
        #    parameters = [parameters[0]]
        for param in parameters:
            pr, d, n, pa = self._read_quantizer_params(param)
            prune_range_list.append(pr)
            detrending_list.append(d)
            normalization_list.append(n)
            partition_list.append(pa)

        parameter_zip = zip(prune_range_list, detrending_list, normalization_list,
                            partition_list)
        parameters = {}
        for pr, d, n, pa in parameter_zip:
            key = self._write_quantizer_params(pr, d, n, pa)
            param_set = {'prune_range': pr,
                         'detrending': d,
                         'normalization': n,
                         'partition': pa}
            parameters[key] = param_set

            # don't include duplicate quantizations
            if key not in self._feature_order:
                self._feature_order.append(key)
        self.parameters = parameters

        self._fitted = True

    def transform(self, data_file, output_type='matrix'):
        """

        """
        assert self._fitted, ("'fit()' or 'fit_transform()' must be called"
                              + " prior to running 'transform()'")


        data_name = os.path.basename(data_file)
        data_prefix = os.path.basename(data_name) + '_'
        qdata_dir = tempfile.mkdtemp(prefix=data_prefix,
                                     dir=self.quantized_data_dir)
        data = {}
        data[data_name] = {}
        data[data_name]['files'] = {}
        data[data_name]['directory'] = qdata_dir

        # TODO: TESTING 
        partition_total = len(self.parameters)
        partition_fail_num = 0
        # TODO: END TESTING

        num_xgen_quantizations = 0
        #for i, name in enumerate(self._feature_order):
        for name, p_dict in self.parameters.items():
            p_dict = self.parameters[name]
            data_with_params = data_prefix + name
            data_with_params_path = os.path.join(qdata_dir, data_with_params)
            success = self._try_apply_quantizer(data_file,
                                                outfile=data_with_params_path,
                                                **p_dict)

            #if self._featurization is not None and self._featurization != xgenesess:
            if self._featurization is not None:
                if not success:
                    # TODO: verbosity option needed here
                    partition_fail_num += 1
                    print('Partition failed for: {}'.format(data_name))
                    print('Corresponding quantization:')
                    pprint_dict(p_dict, indent=4)

                    #self._feature_order.remove(name)
                    self._partition_success_set.remove(name)
                    continue
                else:
                    self._partition_success_set.add(name)
                    data_with_params_path = (
                        self._featurization(data_with_params_path,
                                            **self._featurization_params)
                    )
            #elif (self._featurization == xgenesess) and (self.training_X is not
            #                                             None) and (i == 0):
            #    num_training_samples = self.training_X.shape[0]
            #    with open(data_with_params_path, 'r') as infile:
            #        num_test_samples = sum(1 for _ in infile)
            #    total_samples = num_training_samples + num_test_samples
            #    one_line = dict(self._featurization_params)
            #    one_line['num_lines'] = 'one'

            #    start_time = time()
            #    data_with_params_path = (
            #        self._featurization(data_with_params_path,
            #                            **one_line)
            #    )
            #    end_time = time()
            #    hours = (end_time - start_time) / 3600

            #    num_quantizations = int(xgenesess_hours
            #                            * len(self._feature_order)
            #                            / (hours * total_samples)) - 1
            #    if num_quantizations <= 0:
            #        print('WARNING: dataset might be too large for' +
            #              ' time allotted to XgenESeSS.')
            #        num_quantizations = 1
            #elif (self._featurization == xgenesess) and (self.training_X is not
            #                                             None) and (i != 0):
            #    if not success or num_xgen_quantizations > num_quantizations:
            #        # TODO: verbosity option needed here
            #        partition_fail_num += 1
            #        if not success:
            #            print('Partition failed for: {}'.format(data_name))
            #        elif num_xgen_quantizations > num_quantizations:
            #            print('Partition failed for due to time: {}'.format(data_name))
            #        print('Corresponding quantization:')
            #        pprint_dict(p_dict, indent=True)

            #        #self._feature_order.remove(name)
            #        self._partition_success_set.remove(name)
            #        continue
            #    elif num_xgen_quantizations < num_quantizations:
            #        self._partition_success_set.add(name)
            #        data_with_params_path = (
            #            self._featurization(data_with_params_path,
            #                                **self._featurization_params)
            #        )
            elif self._gsmash:
                alphabet_size = len(p_dict['partition']) + 1
                genesess_libfile(data_with_params_path, alphabet_size,
                                 gen_epsilon=self._gen_epsilon,
                                 num_steps=self._num_steps,
                                 num_models=self._num_models,
                                 runfile=True)

            data_with_params_name = os.path.basename(data_with_params_path)
            data[data_name]['files'][name] = (
                os.path.basename(data_with_params_name)
            )

        #if self.training_X is not None and self._featurization == xgenesess:
        #    for training_name, files in data.items():
        #        if training_name != data_name:
        #            for name in self._feature_order:
        #            #for name, p_dict in self.parameters.items():
        #                p_dict = self.parameters[name]
        #                data_with_params = training_name + name
        #                data_with_params_path = os.path.join(qdata_dir, data_with_params)
        #                data_with_params_path = (
        #                    self._featurization(data_with_params_path,
        #                                        **self._featurization_params)
        #                )
        #                data_with_params_name = os.path.basename(data_with_params_path)
        #                data[data_name]['files'][name] = (
        #                    os.path.basename(data_with_params_name)
        #                )


        # TODO: verbose option needed here
        if self._featurization is not None:
            if partition_fail_num == 0 and self._featurization is not None:
                print('No partitions failed for {}!'.format(data_name))
            else:
                print('{}/{} partitions failed.'.format(partition_fail_num,
                                                        partition_total))

            if partition_fail_num == partition_total:
                print(('ALL PARTITIONS FAILED.\nCurrent problem cannot be'
                       + ' solved using d3m_datasmash.XG1() or'
                       + ' d3m_datasmash.XG2().\nUse any of the other'
                       + ' d3m_datasmash classifiers. Outputting random'
                       + ' predictions.'))
                return None

        X = self.combine_data(data, output_type=output_type)
        #if self.training_X is None:
        #    self.training_X = X
        #    print(X.shape)
        #else:
        #if self.training_X is not None:
        #valid_indices = [i for parameter, index in
        #                 self.parameter_index_map.items() for i in index if
        #                 parameter ]
        if self.training_X is not None:
            valid_indices = []
            all_indices = []
            for parameter, index in self.parameter_index_map.items():
                if parameter in self._partition_success_set:
                    #print(index[0], index[-1])
                    valid_indices += index
                all_indices += index
            valid_indices = sorted(valid_indices)
            self.training_X = self.training_X[:, valid_indices]

        return X

    def fit_transform(self, data_dir, output_type='matrix'):
        """

        """
        self.fit(data_dir)

        #lib_list = self.data #list(self.data.keys())
        X = []
        for lib_file in self.data: #lib_list:
            lib_path = os.path.join(data_dir, lib_file)
            X_ = self.transform(lib_path, output_type=output_type)
            if X_ is None:
                return None
            X.append(X_)
        X_ = np.vstack(X)
        if output_type == 'filename':
            X_ = X
        self.training_X = X_
        return X_

    @staticmethod
    def _get_row_col_nums(data_file):
        """

        """

    @staticmethod
    def _get_data_size(data_dir):
        """

        """
        library_list = os.path.join(data_dir, 'library_list')
        dataset = os.path.join(data_dir, 'dataset')
        if os.path.isfile(library_list):
            with open(library_list, 'r') as infile:
                data = [os.path.join(data_dir, ll.split(' ')[0]) for ll in infile]
        elif os.path.isfile(dataset):
            data = [dataset]

        num_rows = 0
        max_num_cols = 0
        for data_file in data:
            with open(data_file, 'r') as infile:
                for row in infile:
                    num_rows += 1
                    cols = len(row.split(' '))
                    if cols > max_num_cols:
                        max_num_cols = cols
        return num_rows, max_num_cols

    def _get_sample_size(self, data_dir):
        """

        """
        num_train_samples, max_length = self._get_data_size(data_dir)
        if self._multi_partition:
            qs = 96
        else:
            qs = 1
        sample_size = self._core_hours * (10 ** 7) / (1.48 * max_length * qs)
        sample_size = (sample_size ** (1 / 2)) / (num_train_samples)
        return sample_size

    def combine_data(self, data_dict, output_type='matrix'):
        """

        """
        assert self._fitted, ("'fit()' or 'fit_transform()' must be called"
                              + " prior to calling 'transform()'")
        X = []
        X2 = []
        index_start = 0

        for i, (lib_file, feat_files) in enumerate(data_dict.items()):
            matrix_list = []
            matrix_list2 = []
            feat_dir = feat_files['directory']
            for f in self._feature_order:
                if f in feat_files['files']:
                    feat_file_path = os.path.join(feat_dir,
                                                  feat_files['files'][f])
                    wait_for_file(feat_file_path)
                    #print(feat_file_path)
                    matrix = np.loadtxt(feat_file_path)

                    # in case one of the feature files is only one line, we
                    # need to reshape it to be a matrix (otherwise np.loadtxt
                    # will just return us a list)
                    if matrix.ndim == 1:
                        matrix = matrix.reshape((1, len(matrix)))
                    #matrix2 = pd.read_csv(feat_file_path, sep=' ', header=None)

                    # (X)genESeSS feature files end each line with a space
                    # -> the last column when loading from pandas is just NaNs
                    # -> -> we drop the last column
                    #matrix2.drop(matrix2.columns[-1], axis=1, inplace=True)

                    if output_type == 'matrix':
                        matrix_list.append(matrix)
                    elif output_type == 'filename':
                        lib = feat_file_path
                    #matrix_list2.append(matrix2)
                else:
                    continue

                if i == 0 and self.training_X is None:
                    col_len = np.shape(matrix)[1]
                    index_end = index_start + col_len
                    index_range = list(range(index_start, index_end))
                    self.parameter_index_map[f] = index_range
                    index_start = index_end

            if output_type == 'matrix':
                X_ = pd.DataFrame(np.hstack(matrix_list))
                #X_2 = pd.concat(matrix_list2, axis=1)
                X.append(X_)
                #X2.append(X_2)
            else:
                # currently output_type='filename' only supports one partition
                X = lib
        #X = np.vstack(X)
        if output_type == 'matrix':
            X = pd.concat(X, axis=0, ignore_index=True)
        #print(X.shape)
        #print(X2.shape)
        return X


    @staticmethod
    def _line_by_line(data_file, *, function, **kwargs):
        """

        """
        directory = os.path.dirname(os.path.realpath(data_file))
        tmp_dir = tempfile.mkdtemp(dir=directory)

        feature_file = data_file + '_features'
        with open(data_file, 'r') as infile:
            for i, line in enumerate(infile):
                line_file = os.path.join(tmp_dir, str(i))
                with open(line_file, 'w') as outfile:
                    outfile.write(line)
                new_line_file = function(line_file, **kwargs)
                lines = []

                wait_for_file(new_line_file)

                with open(new_line_file, 'r') as infile:
                    for line_ in infile:
                        lines.append(line_)
                with open(feature_file, 'a+') as outfile:
                    for line__ in lines:
                        outfile.write(line__)
        #rmtree(tmp_dir)
        return feature_file

    def _get_command_list(self, data_dir):
        """

        """
        problem_type = ['-t']
        num_streams = ['-T']
        if self._problem_type == 2 or self._problem_type == 'supervised':
            problem_type.append("2")
            num_streams.append("-1")
        else:
            num_streams.append(str(self._num_streams))
            if self._problem_type == 1 or self._problem_type == 'unsupervised_with_targets':
                problem_type.append("1")
            elif self._problem_type == 0 or self._problem_type == 'unsupervised':
                problem_type.append("0")

        quantizer_path = os.path.join(self._bin_path, 'Quantizer')
        quantizer_binary = [os.path.abspath(quantizer_path)]
        data_dir = ['-D', data_dir]

        sample_size = ['-x', str(self._sample_size)]

        pooled = ['-w']
        if self._pooled:
            pooled.append("1")
        else:
            pooled.append("0")

        epsilon = ['-e', str(self._epsilon)]

        min_alphabet_size = ['-a', str(self._min_alphabet_size)]
        max_alphabet_size = ['-A', str(self._max_alphabet_size)]

        if self._detrending is not None:
            detrending = ['-d', str(self._detrending)]
        else:
            detrending = []

        if self._normalization is not None:
            normalization = ['-n', str(int(self._normalization))]
        else:
            normalization = []

        if not self._multi_partition:
            num_partitions = ['-M', '1']
        else:
            num_partitions = []

        command_list = (quantizer_binary
                        + data_dir
                        + problem_type
                        #+ num_streams # TODO: testing Quantizer_v1
                        + sample_size
                        #+ pooled # TODO: testing Quantizer_v1
                        + epsilon
                        + min_alphabet_size
                        + max_alphabet_size
                        + detrending
                        + normalization
                        + num_partitions)
        self._command_list = command_list

    def _note_lib_files(self, data_dir):
        """

        """
        library_list = os.path.join(data_dir, 'library_list')
        if os.path.isfile(library_list):
            train_data = [row.split(' ')[:2] for row in
                          open(library_list).read().splitlines()]
        else:
            train_data = [['dataset', -1]]
        for lib, label_str in train_data:
            self.data.append(lib)
            #self.data[lib] = {}
            #self.data[lib]['files'] = {}
            #self.data[lib]['label'] = int(label_str)

    @staticmethod
    def _detrend(df, *, detrend_level):
        """

        """
        return df.diff(axis=1).dropna(how='all', axis=1)

    @staticmethod
    def _normalize(df):
        """

        """
        standard_normal_rows = df.subtract(df.mean(axis=1),
                                           axis=0).divide(df.std(axis=1),
                                                          axis=0)
        return standard_normal_rows

    @staticmethod
    def _prune(df, lower_bound, upper_bound):
        """

        """
        for index in df.index:
            X = []
            for val in df.iloc[index].values:
                if val <= float(lower_bound) or val >= float(upper_bound):
                    X = np.append(X,val)
            pruned_ = np.empty([1, len(df.iloc[index].values) - len(X)])
            pruned_[:] = np.nan
            X = np.append(X, pruned_)
            df.loc[index] = X
        return df

    def _try_apply_quantizer(self, filename, *, partition, prune_range=None,
                             detrending=None, normalization=None, outfile=None,
                             verbose=False):
        """

        """
        max_col_len = 0
        with open(filename, 'r') as infile:
            csv_reader = csv.reader(infile, delimiter=' ')
            for row in csv_reader:
                len_ = len(row)
                if len_ > max_col_len:
                    max_col_len = len_
        unquantized = pd.read_csv(filename, delimiter=' ', dtype='float',
                                  header=None, names=range(max_col_len))

        if prune_range:
            if verbose:
                print('PRUNING')
            unquantized = self._prune(unquantized, prune_range[0], prune_range[1])
        if detrending:
            if verbose:
                print('DETRENDING')
            unquantized = self._detrend(unquantized, detrend_level=detrending)
        if normalization:
            if verbose:
                print('NORMALIZING')
            unquantized = self._normalize(unquantized)

        if outfile is None:
            _outfile = filename
        else:
            _outfile = outfile
        quantized = np.digitize(unquantized, bins=partition)
        #np.savetxt(_outfile, quantized, fmt='%d', delimiter=' ')
        pd.DataFrame(quantized).to_csv(_outfile, sep=' ', index=False, header=False)

        wait_for_file(_outfile)

        if self._correct_num_symbols(quantized, partition):
            return 1
        else:
            return 0


    @staticmethod
    def _correct_num_symbols(quantized_matrix, partition):
        """

        """
        expected_num_symbols = len(partition) + 1
        i = 0
        for row in quantized_matrix:
            num_symbols = len(np.unique(row))
            if num_symbols != expected_num_symbols:
                return False
            i += 1

        return True


    @staticmethod
    def _read_quantizer_params(parameters):
        """

        """
        parameters_ = parameters.split('L')[0]
        prune_range = []
        for index, char in enumerate(parameters_):
            if char == 'R':
                for char_ in parameters_[index+2:]:
                    if char_ != ']':
                        prune_range.append(char_)
                    else:
                        break
            elif char == 'D':
                detrending = int(parameters_[index+1])
            elif char == 'N':
                normalization = int(parameters_[index+1])
        if prune_range:
            prune_range = ''.join(prune_range).split(' ')

        partition = parameters_.split('[')[-1].strip(']').split()
        no_negative_zero_partition = []
        for p in partition:
            if repr(float(p)) == '-0.0':
                p_ = p[1:]
            else:
                p_ = p
            no_negative_zero_partition.append(p_)

        return prune_range, detrending, normalization, no_negative_zero_partition

    @staticmethod
    def _write_quantizer_params(prune_range, detrending, normalization,
                                partition):
        """

        """
        params = []
        if prune_range:
            params.append('R')
            params += prune_range
        if detrending:
            params.append('D')
            params.append(detrending)
        if normalization:
            params.append('N')
            params.append(normalization)
        if partition:
            params.append('P')
            params += str([float(p) for p in partition]).replace(' ', '')
        params_string = ''.join([str(p) for p in params])
        return params_string

    @staticmethod
    def _get_num_cols(infile):
        with open(infile) as f:
            first_line = f.readline()
        first_line_list = first_line.strip.split(' ')
        num_col = len(first_line_list)
        return num_col

