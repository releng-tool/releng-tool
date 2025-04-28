# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections import defaultdict
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import debug
from releng_tool.util.log import verbose
from time import monotonic
import math
import os
import pickle

# optional imports
try:
    # disable xwindows backend (as it is not required and may cause issue with
    # systems without a display configured)
    import matplotlib as mpl
    mpl.use('Agg')

    import matplotlib.pyplot as plt
    import numpy as np
    has_matplotlib = True
except ImportError:
    has_matplotlib = False

# filename for the statistics database
STATISTICS_NAME = 'statistics.dat'


class RelengStats:
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
            debug('loaded statistics')
        except OSError:
            verbose('failed to load original statistics (io error)')
        except ValueError:
            verbose('failed to load original statistics (pickle error)')

    def save(self, desc=None):
        """
        save statistics for future reference

        Will save any statistics which should be persisted for future
        considerations. This is to help render a "complete" report of statistics
        when re-running releng-tool with packages which may already been
        completed.

        Args:
            desc (optional): description of this save event (for logging)
        """

        if not mkdir(self.out_dir):
            verbose('unable to generate output directory for statistics')
            return

        if desc:
            desc = f' ({desc})'
        else:
            desc = ''

        try:
            with open(self.dat_file, 'wb') as f:
                pickle.dump(self.data, f, protocol=2)  # 2 for py2/py3 support
            debug('saved statistics' + desc)
        except OSError:
            verbose('failed to save statistics' + desc)

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
        self.cache[pkg][stage]['start'] = monotonic()

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
        end_time = monotonic()
        start_time = self.cache[pkg][stage]['start']

        if 'duration' not in self.data:
            self.data['duration'] = {}
        if pkg not in self.data['duration']:
            self.data['duration'][pkg] = {}
        if stage not in self.data['duration'][pkg]:
            self.data['duration'][pkg][stage] = {}

        self.data['duration'][pkg][stage] = end_time - start_time

        if save:
            self.save(desc=f'{pkg}-{stage}')

    def generate(self):
        """
        generate a final report of statistics

        To be invoked at the end of a releng-tool process, this call will
        generate reports/etc. for any tracked statistics information based on
        the current and previous invoked executions (if any).
        """
        if not mkdir(self.out_dir):
            verbose('unable to generate output directory for statistics')
            return

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

        ordered_categories = [
            'boot',
            'fetch',
            'extract',
            'fetch-post',
            'patch',
            'configure',
            'build',
            'install',
            'post',
        ]

        for ordered_category in ordered_categories:
            if ordered_category not in categories:
                ordered_categories.remove(ordered_category)
        for category in categories:
            if category not in ordered_categories:
                ordered_categories.append(category)
        categories = ordered_categories

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
                        value = durations[pkg].get(category, 0)
                        f.write(',' + str(int(value)))
                    f.write('\n')
        except OSError as e:
            verbose('failed to write duration statistics: {}', e)

        # duration statistics to plot (if available)
        generate_pdf = True

        if not has_matplotlib:
            generate_pdf = False
            debug('duration statistics plot not supported (no matplotlib)')
        elif isinstance(mpl.__version__, tuple) and mpl.__version__ < (2, 1):
            generate_pdf = False
            debug('duration statistics plot not supported (old matplotlib)')
        elif 'releng.stats.no_pdf' in self.opts.quirks:
            generate_pdf = False
            debug('duration statistics plot disabled by quirk')

        if generate_pdf:
            verbose('generating duration statistics (pdf)...')

            BAR_HEIGHT = 0.4
            EXTRA_HEIGHT = 1
            FIG_WIDTH = 10
            fig_height_pkgs = (BAR_HEIGHT + EXTRA_HEIGHT) * len(pkgs)
            fig_height_total = (BAR_HEIGHT + EXTRA_HEIGHT) * (len(pkgs) + 1)

            figsize_pkgs = (FIG_WIDTH, fig_height_pkgs)
            figsize_total = (FIG_WIDTH, fig_height_total)

            fig_pkgs, ax_pkgs = plt.subplots(figsize=figsize_pkgs)
            fig_total, ax_total = plt.subplots(figsize=figsize_total)
            axs = [ax_pkgs, ax_total]
            figs = [fig_pkgs, fig_total]

            pkgs.reverse()
            pkgs_total = list(pkgs)
            pkgs_total.insert(0, 'total')

            offset = [0] * len(pkgs)
            offset_total = [0] * len(pkgs_total)
            for category in categories:
                width = []
                width_total = []
                total = 0

                for pkg in pkgs:
                    if category in durations[pkg]:
                        duration = durations[pkg][category]
                        width.append(duration)
                        width_total.append(duration)
                        total += duration
                    else:
                        width.append(0)
                        width_total.append(0)
                width_total.insert(0, total)

                ax_pkgs.barh(pkgs, width, height=BAR_HEIGHT,
                    left=offset, label=category)
                ax_total.barh(pkgs_total, width_total, height=BAR_HEIGHT,
                    left=offset_total, label=category)
                offset = np.add(offset, width)
                offset_total = np.add(offset_total, width_total)

            # provide some spacing near the right
            MIN_OFFSET = 10

            xlim = round(math.ceil(max(offset) / 10.)) * 10
            if xlim - max(offset) < MIN_OFFSET:
                xlim += MIN_OFFSET
            ax_pkgs.set_xlim([0, xlim])

            xlim_total = round(math.ceil(max(offset_total) / 10.)) * 10
            if xlim_total - max(offset_total) < MIN_OFFSET:
                xlim_total += MIN_OFFSET
            ax_total.set_xlim([0, xlim_total])

            # labels
            for ax in axs:
                ax.set_title('Package Stage Durations')
                ax.set_xlabel('Duration (seconds)')
                ax.legend()
                ax.grid(axis='x', linestyle=':', linewidth=0.4)

            # ensure rotated labels state in render area
            for fig in figs:
                fig.tight_layout()

            # generate figures
            dur_pdf = os.path.join(self.out_dir, 'durations.pdf')
            fig_pkgs.savefig(dur_pdf)

            dur_pdf_total = os.path.join(self.out_dir, 'durations-total.pdf')
            fig_total.savefig(dur_pdf_total)

            # close/cleanup figures
            plt.close()
