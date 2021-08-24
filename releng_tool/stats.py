# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from collections import defaultdict
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.log import debug
from releng_tool.util.log import verbose
import math
import os
import pickle

try:
    from time import clock as capture_clock
except ImportError:
    from time import monotonic as capture_clock

# optional imports
try:
    import matplotlib.pyplot as plt
    import numpy
    has_matplotlib = True
except ImportError:
    has_matplotlib = False

# filename for the statistics database
STATISTICS_NAME = 'statistics.dat'

class RelengStats():
    """
    statistics tracking

    Registry provides a means for external implementation to hook into various
    stages of a release engineering process.

    Args:
        opts: options used to configure the engine

    Attributes:
        cache: cache of statistics for this runtime
        dat_file: file to store persisted statistics
        data: dictionary of data that can be persisted
        opts: options used to configure the engine
        out_dir: directory to generate final statistics to
    """
    def __init__(self, opts):
        self.cache = defaultdict(lambda: defaultdict(dict))
        self.opts = opts
        self.out_dir = os.path.join(self.opts.out_dir, 'misc')
        self.dat_file = os.path.join(self.out_dir, STATISTICS_NAME)

        self.data = {}

    def load(self):
        """
        load any persisted statistics

        Will load any statistics which may have been persisted from a previous
        run. This is to help render a "complete" report of statistics when
        re-running releng-tool with packages which may already been completed.
        """
        if not os.path.exists(self.dat_file):
            return

        try:
            with open(self.dat_file, 'rb') as f:
                self.data = pickle.load(f)
        except IOError:
            verbose('failed to load original statistics (io error)')
        except ValueError:
            verbose('failed to load original statistics (pickle error)')

    def save(self):
        """
        save statistics for future reference

        Will save any statistics which should be persisted for future
        considerations. This is to help render a "complete" report of statistics
        when re-running releng-tool with packages which may already been
        completed.
        """
        try:
            with open(self.dat_file, 'wb') as f:
                pickle.dump(self.data, f, protocol=2) # 2 for py2/py3 support
        except IOError:
            verbose('failed to save statistics')

    def track_duration_start(self, pkg, stage):
        """
        track a duration start

        To be invoked when tracking the start of a package event for a given
        stage. This call is to be used with ``track_duration_end``, to help
        track the duration of a package's stage.

        Args:
            pkg: the package
            stage: the stage which has started
        """
        self.cache[pkg][stage]['start'] = capture_clock()

    def track_duration_end(self, pkg, stage, save=True):
        """
        track a duration end

        To be invoked when tracking the end of a package event for a given
        stage. This call is to be used with ``track_duration_start``, to help
        track the duration of a package's stage.

        Args:
            pkg: the package
            stage: the stage which has ended
            save (optional): automatically save the duration (default: True)
        """
        end_time = capture_clock()
        start_time = self.cache[pkg][stage]['start']

        if 'duration' not in self.data:
            self.data['duration'] = {}
        if pkg not in self.data['duration']:
            self.data['duration'][pkg] = {}
        if stage not in self.data['duration'][pkg]:
            self.data['duration'][pkg][stage] = {}

        self.data['duration'][pkg][stage] = end_time - start_time

        if save:
            self.save()

    def generate(self):
        """
        generate a final report of statistics

        To be invoked at the end of a releng-tool process, this call will
        generate reports/etc. for any tracked statistics information based on
        the current and previous invoked executions (if any).
        """
        if not ensure_dir_exists(self.out_dir):
            verbose('unable to generate output directory for statistics')
            return None

        self._generate_duration()

    def _generate_duration(self):
        """
        generate duration-related statistics

        When generating a statistics report, this call creating/adds information
        about durations which may have been captured.
        """

        if 'duration' not in self.data:
            return

        durations = self.data['duration']

        pkgs = list(durations.keys())
        pkgs = sorted(pkgs)

        categories = set()
        for pkg_data in durations.values():
            categories.update(pkg_data.keys())
        categories = sorted(categories)

        # duration statistics to csv
        verbose('generating duration statistics (csv)...')
        dur_csv = os.path.join(self.out_dir, 'durations.csv')
        try:
            with open(dur_csv, 'w') as f:
                # header
                f.write('# pkg')
                for category in categories:
                    f.write(',' + category)
                f.write('\n')

                # data
                for pkg in pkgs:
                    f.write(pkg)

                    for category in categories:
                        if category in durations[pkg]:
                            value = durations[pkg][category]
                        else:
                            value = 0
                        f.write(',' + str(int(value)))
                    f.write('\n')
        except IOError as e:
            verbose('failed to write duration statistics: {}', e)

        # duration statistics to plot (if available)
        if has_matplotlib:
            verbose('generating duration statistics (pdf)...')
            fig_pkgs, ax_pkgs = plt.subplots()
            fig_total, ax_total = plt.subplots()
            axs = [ax_pkgs, ax_total]
            figs = [fig_pkgs, fig_total]
            BAR_WIDTH = 0.3

            pkgs_total = list(pkgs)
            pkgs_total.append('total')

            offset = [0] * len(pkgs)
            offset_total = [0] * len(pkgs_total)
            for category in categories:
                height = []
                height_total = []
                total = 0
                for pkg in pkgs:
                    if category in durations[pkg]:
                        duration = durations[pkg][category]
                        height.append(duration)
                        height_total.append(duration)
                        total += duration
                    else:
                        height.append(0)
                        height_total.append(0)
                height_total.append(total)

                ax_pkgs.bar(pkgs, height, width=BAR_WIDTH,
                    bottom=offset, label=category)
                ax_total.bar(pkgs_total, height_total, width=BAR_WIDTH,
                    bottom=offset_total, label=category)
                offset = numpy.add(offset, height)
                offset_total = numpy.add(offset_total, height_total)

            # provide some spacing near the top
            ylim = int(math.ceil(max(offset) / 10.)) * 10
            ax_pkgs.set_ylim([0, ylim])

            ylim_total = int(math.ceil(max(offset_total) / 10.)) * 10
            ax_total.set_ylim([0, ylim_total])

            # labels
            for ax in axs:
                ax.set_ylabel('Duration (seconds)')
                ax.set_title('Package Stage Durations')
                ax.legend()

            # rotate x-labels or package names may overlap
            for ax in axs:
                for tick in ax.get_xticklabels():
                    tick.set_rotation(90)

            # ensure rotated labels state in render area
            for fig in figs:
                fig.tight_layout()

            # generate figures
            dur_pdf = os.path.join(self.out_dir, 'durations.pdf')
            fig_pkgs.savefig(dur_pdf)

            dur_pdf_total = os.path.join(self.out_dir, 'durations-total.pdf')
            fig_total.savefig(dur_pdf_total)
        else:
            debug('duration statistics plot not supported')
