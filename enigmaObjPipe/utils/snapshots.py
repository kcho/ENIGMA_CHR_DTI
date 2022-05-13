import sys
sys.path.append('/Users/kc244/nifti-snapshot')
from nifti_snapshot import nifti_snapshot


class Snapshot(object):
    def snapshot_first_b0(self, input_file, label,
                          cbar_title='intensity',
                          intensity_percentile=(5, 95), force=False):
        self.screen_shot_dir.mkdir(exist_ok=True, parents=True)
        output_file_loc = self.screen_shot_dir / f"{label}.jpg"
        title = f"{self.subject_name} {label} " \
                f"(1st B0 volume={self.b0_index[0]})"

        if force or not output_file_loc.is_file():
            _ = nifti_snapshot.SimpleFigure(
                    image_files=[input_file],
                    title=title,
                    make_transparent_zero=True,
                    cbar_width=0.5,
                    cbar_title=cbar_title,
                    output_file=output_file_loc,
                    volumes=[self.b0_index[0]],
                    percentile=intensity_percentile)

    def snapshot_tbss(self, input_file, label,
                      cbar_title='intensity',
                      intensity_percentile=(5, 95), force=False):
        self.tbss_screen_shot_dir.mkdir(exist_ok=True, parents=True)
        output_file_loc = self.tbss_screen_shot_dir / f"{label}.jpg"
        title = f"TBSS {label}"

        if force or not output_file_loc.is_file():
            tbssFigure = nifti_snapshot.TbssFigure(
                image_files=[input_file],
                output_file=output_file_loc,
                cmap_list=["Blues_r"],
                cbar_titles=[cbar_title],
                alpha_list=[0.8],
                title=title,
                cbar_x=0.35,
                cbar_width=0.3)

            tbssFigure.create_figure_one_map()

    def snapshot_tbss_gb(self, input_file, background_file, label,
                      cbar_title='intensity',
                      intensity_percentile=(5, 95),
                      cmap='Greens',
                      force=False):
        self.tbss_screen_shot_dir.mkdir(exist_ok=True, parents=True)
        output_file_loc = self.tbss_screen_shot_dir / f"{label}.jpg"
        title = f"TBSS {label}"

        # if force or not output_file_loc.is_file():
        tbssFigure = nifti_snapshot.TbssFigure(
            image_files=[input_file],
            template_FA=background_file,
            output_file=output_file_loc,
            cmap_list=[cmap],
            cbar_titles=[cbar_title],
            alpha_list=[0.8],
            title=title,
            cbar_x=0.35,
            tbss_filled=True,
            intensity_percentile=intensity_percentile,
            cbar_width=0.3,
            dpi=300)

        tbssFigure.create_figure_non_p_map()


    def snapshot_diff_first_b0(self, input_file_1, input_file_2,
                               label_1, label_2,
                               cbar_title='intensity',
                               intensity_percentile=(5, 95), force=False):
        self.screen_shot_dir.mkdir(exist_ok=True, parents=True)

        output_file_loc = self.screen_shot_dir / \
                f"{label_1}_minus_{label_2}.jpg"

        title = f"{self.subject_name} {label_1} - {label_2} " \
                f"(1st B0 volume={self.b0_index[0]})"

        if force or not output_file_loc.is_file():
            _ = nifti_snapshot.SimpleFigure(
                    image_files=[input_file_1, input_file_2],
                    title=title,
                    make_transparent_zero=False,
                    cmap_list=['viridis'],
                    cbar_width=0.5,
                    cbar_title=cbar_title,
                    output_file=output_file_loc,
                    volumes=[self.b0_index[0]],
                    percentile=intensity_percentile,
                    get_diff=True)

