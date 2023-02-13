import shutil

class MaskingPipe(object):
    def cnn_brain_masking(self, force: bool = False, nproc: int = 1):
        if force or not self.diff_mask.is_file():
            # new masking using CNN masking
            # self.CNN_brain_extraction(self.diff_raw_dwi, self.diff_mask)
            shutil.copy(self.diff_raw_bval,
                        str(self.diff_dwi_unring).split('.')[0] + '.bval')
            shutil.copy(self.diff_raw_bvec,
                        str(self.diff_dwi_unring).split('.')[0] + '.bvec')
            self.CNN_brain_extraction(self.diff_dwi_unring,
                                      self.diff_mask,
                                      nproc=nproc)


