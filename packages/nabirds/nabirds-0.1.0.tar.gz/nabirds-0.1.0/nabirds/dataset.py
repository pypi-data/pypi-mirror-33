from imageio import imread
import numpy as np


class Dataset(object):
	def __init__(self, uuids, annotations):
		super(Dataset, self).__init__()
		self.uuids = uuids
		self._annot = annotations

	def __len__(self):
		return len(self.uuids)

	def _get(self, method, i):
		return getattr(self._annot, method)(self.uuids[i])



	def get_example(self, i, mode="RGB"):
		methods = ["image", "parts", "label"]
		im_path, parts, label = [self._get(m, i) for m in methods]
		return imread(im_path, pilmode=mode), parts, label

	__getitem__  = get_example


# some convention functions

def __expand_parts(p):
	return p[:, 0], p[:, 1:3], p[:, 3].astype(bool)

def visible_part_locs(p):
	idxs, locs, vis = __expand_parts(p)
	return idxs[vis], locs[vis].T

def visible_crops(im, p, ratio=np.sqrt(49 / 400), padding_mode="edge"):
	assert im.ndim == 3, "Only RGB images are currently supported!"
	idxs, locs, vis = __expand_parts(p)
	h, w, c = im.shape
	crop_h = crop_w = int(np.sqrt(h*w) * ratio)
	crops = np.zeros((len(idxs), crop_h, crop_w, c), dtype=im.dtype)

	padding = np.array([crop_h, crop_w]) // 2

	padded_im = np.pad(im, [padding, padding, [0,0]], mode=padding_mode)

	for i, loc, is_vis in zip(*__expand_parts(p)):
		if not is_vis: continue
		x0, y0 = loc - crop_h // 2 + padding
		crops[i] = padded_im[y0:y0+crop_h, x0:x0+crop_w]

	return crops

