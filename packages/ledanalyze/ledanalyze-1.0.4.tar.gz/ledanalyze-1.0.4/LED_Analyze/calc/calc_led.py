"""
LED_Analyze - calc_basic
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0
"""
import numpy as np
from os.path import exists

from analysis_main import DataObject
from calc.calc_common import CalcProcess

class CropCtr(CalcProcess):
    """
    Take an array of luminance data which is assumed to be a bright
    light on a background of dark noise. Take a 16x16 sample of the
    dark noise from the upper left corner of the array. Using this data
    determine a noise gate, as well as a count threshold, find the
    center of the light, and crop to within a specified distance.
    """
    
    gui_commands = [
        ("SelectNameLabelFrame",
         ("lum_in", "out_name_lum", "out_lum_to_db"),
         ("Input:", "Output Name:", "Luminance Data", 400, (60, 100)),
         True),
        ("SelectNameLabelFrame",
         ("c_x_in", "out_name_x", "out_x_to_db"),
         ("Input:", "Output Name:", "Chromaticity X Data", 400, (60, 100)),
         True),
        ("SelectNameLabelFrame",
         ("c_y_in", "out_name_y", "out_y_to_db"),
         ("Input:", "Output Name:", "Chromaticity Y Data", 400, (60, 100)),
         True),
        ("SelectNameLabelFrame",
         (("x_min_in",
           "x_max_in",
           "y_min_in",
           "y_max_in"), "out_name_dims", "out_dims_to_db"),
         (("Hor. Min:",
           "Hor. Max",
           "Vert. Min:",
           "Vert. Max:"), "Output Name:", "Dimensions", 400, (60, 100)),
         False),
        ("SpboxFrame", "count", ("Threshold:", list(range(1, 33)), 200, 75)),
        ("SpboxFrame", "dist", ("Margin:", list(range(0, 65)), 200, 75)),
        ("SpboxFrame", "rotate", ("Rotate:", [0, 90, 180, 270], 200, 75))]
    
    def __init__(
            self, out_name_lum, out_name_x, out_name_y, out_name_dims, 
            out_lum_to_db, out_x_to_db, out_y_to_db, out_dims_to_db,
            lum_in, c_x_in, c_y_in, x_min_in, x_max_in, y_min_in, y_max_in, 
            count, dist, rotate):
        
        self.name = "Center Crop "
        self.lum_in = lum_in
        self.c_x_in = c_x_in
        self.c_y_in = c_y_in
        self.out_name_lum = out_name_lum
        self.out_name_x = out_name_x
        self.out_name_y = out_name_y
        self.out_name_dims = out_name_dims
        self.out_lum_to_db = out_lum_to_db
        self.out_x_to_db = out_x_to_db
        self.out_y_to_db = out_y_to_db
        self.out_dims_to_db = out_dims_to_db
        self.x_min_in = x_min_in
        self.x_max_in = x_max_in
        self.y_min_in = y_min_in
        self.y_max_in = y_max_in
        self.count = int(count)
        self.dist = int(dist)
        self.rotate = int(rotate)
        
        CalcProcess.__init__(
            self, 
            [lum_in.calc, c_x_in.calc, c_y_in.calc,
             x_min_in.calc, x_max_in.calc, y_min_in.calc, y_max_in.calc])
        
        self.inputs = [
            lum_in.name, c_x_in.name, c_y_in.name, x_min_in.name,
            x_max_in.name, y_min_in.name, y_max_in.name]
        self.outputs.extend([
            DataObject(self.out_name_lum, np.array([]), 
                       self, self.out_lum_to_db),
            DataObject(self.out_name_x, np.array([]), 
                       self, self.out_x_to_db),
            DataObject(self.out_name_y, np.array([]), 
                       self, self.out_y_to_db),
            DataObject(self.out_name_dims, np.array([]), 
                       self, self.out_dims_to_db)])
    
    def check(self):
        
        if len(set(
            (self.out_name_lum, 
             self.out_name_x, 
             self.out_name_y,
             self.out_name_dims))) != 4:
            
            return "Output names must be unique."
        
        else:
            return None
    
    def run(self):
        
        original_rng = self.lum_in.read_data
        c_x_out = self.c_x_in.read_data
        c_y_out = self.c_y_in.read_data
        
        # Handle data rotation
        if self.rotate != 0:
            original_rng = np.rot90(original_rng, int(self.rotate/90))
            c_x_out = np.rot90(c_x_out, int(self.rotate/90))
            c_y_out = np.rot90(c_y_out, int(self.rotate/90))
        
        if self.rotate in (90, 270):
            x_min_in = self.y_min_in.read_data
            x_max_in = self.y_max_in.read_data
            y_min_in = self.x_min_in.read_data
            y_max_in = self.x_max_in.read_data
        else:
            x_min_in = self.x_min_in.read_data
            x_max_in = self.x_max_in.read_data
            y_min_in = self.y_min_in.read_data
            y_max_in = self.y_max_in.read_data
        
        # Sample background noise data around edge of the input data
        noise_sample = np.concatenate((
            original_rng[0,:], 
            original_rng[-1,:],
            original_rng[:,0][1:-1],
            original_rng[:,-1][1:-1]))
        noise_threshold = np.average(noise_sample) + 6 * np.std(noise_sample)
        
        # Count number of elements in each row/column above threshold
        thresh_row = np.array([len(np.where(row > noise_threshold)[0]) \
                      for row in original_rng])
        thresh_col = np.array([len(np.where(col > noise_threshold)[0]) \
                      for col in original_rng.T])
        
        # Get the row/column indices representing the edges of the
        # data above the noise threshold
        i_row = np.where(thresh_row > self.count)[0]
        i_col = np.where(thresh_col > self.count)[0]
        
        x_left = i_col[0]
        x_right = i_col[-1]
        y_top = i_row[0]
        y_bottom = i_row[-1]
        
        width = x_right - x_left
        height = y_bottom - y_top
        ctr_pt_y = int(height/2)
        ctr_pt_x = int(width/2) 
        
        # Extend margins by self.dist, or by as much as the initial
        # size allows
        if x_left - self.dist >= 0:
            x_left -= self.dist
            ctr_pt_x += self.dist
        else:
            x_left = 0
        
        if x_right + self.dist < original_rng.shape[1]:
            x_right += self.dist
        else:
            x_right = original_rng.shape[1]
        
        if y_top - self.dist >= 0:
            y_top -= self.dist
            ctr_pt_y += self.dist
        else:
            y_top = 0
        
        if y_bottom + self.dist < original_rng.shape[0]:
            y_bottom += self.dist
        else:
            y_bottom = original_rng.shape[0]
        
        self.outputs[0].set(original_rng[y_top:y_bottom, x_left:x_right])
        self.outputs[1].set(
            c_x_out[y_top:y_bottom, x_left:x_right])
        self.outputs[2].set(
            c_y_out[y_top:y_bottom, x_left:x_right])
        
        x_dim_in = x_max_in - x_min_in
        y_dim_in = y_max_in - y_min_in
        x_dim_out = x_dim_in * (y_bottom-y_top) / original_rng.shape[0]
        y_dim_out = y_dim_in * (x_right-x_left) / original_rng.shape[1]
        
        self.outputs[3].set(np.array([
            x_dim_out, y_dim_out, width, 
            height, ctr_pt_x, ctr_pt_y, noise_threshold]))

class GenMask(CalcProcess):
    """
    Take an external monochrome image file and an array of luminance data.
    The image is converted to a boolean mask that is manipulated and fitted
    to optimally match the luminance data. 
    """
    thresh_list = list(set(np.logspace(0, 3, 100, dtype=int)))
    thresh_list.sort()
    thresh_list = ["Auto"] + thresh_list
    
    gui_commands = [
        ("ComboboxFrame",
         "lum_in",
         ("Luminance Data:", 300, 120), True),
        ("ComboboxFrame",
         "dims_in",
         ("Dimensions [mm]:", 300, 120), True),
        ("TextEntryFrame", "out_name_mask", ("Mask Name:", 300, 120)),
        ("CheckEntryFrame", "to_db", "Save Mask to DB?"),
        ("TextEntryFrame", "offset", ("Offset [mm]:", 200, 100)),
        ("SpboxFrame", "count", ("Sensitivity:", list(range(1, 33)), 200, 100)),
        ("SpboxFrame", "thresh", 
         ("Step Threshold:", thresh_list, 200, 100))
        ]
    
    def __init__(self, out_name_mask, to_db, lum_in, dims_in, 
                 offset, count, thresh):
        
        self.name = "Generate Mask"
        self.out_name_mask = out_name_mask
        self.to_db = to_db
        self.lum_in = lum_in
        self.dims_in = dims_in
        self.offset = offset
        self.count = count
        self.thresh = thresh
        
        CalcProcess.__init__(self, list(set((lum_in.calc, dims_in.calc))))
        
        self.inputs = [lum_in.name, dims_in.name]
        self.outputs.append(
            DataObject(out_name_mask, np.array([]), self, self.to_db))
    
    def check(self):
        
        try:
            self.offset = float(self.offset)
        except ValueError:
            return "Input offset, angle, width, and height must be a number."
        
        return None
    
    def run(self):
        
        data = self.lum_in.read_data
        mask = np.full(data.shape, True)
        
        edge_list = []
        count = int(self.count)
        test_size = (2*count + 1) ** 2
        
        # Generate the initial mask array using a logarithmic histogram to
        # separate out the illuminated region of the data.
        if self.thresh == "Auto":
            n, bins = np.histogram(
                data, 
                np.logspace(
                    np.log10(2*self.dims_in.read_data[6]), 
                    np.log10(np.max(data)), 
                    int(np.prod(data.shape)**0.5 / 4)))
            i_peak_n = np.argmax(n) + 1
            bin_diff = np.diff(n[np.max((0, i_peak_n-20)) : i_peak_n+1])
            i_max_roc = np.argmax(bin_diff)
            
            i = i_max_roc
            while bin_diff[i] > 0.10 * bin_diff[i_max_roc]:
                i -= 1
            threshold = bins[np.max((0, i_peak_n-20)) + i]
        
        else:
            threshold = int(self.thresh)
        
        for (i, j), val in np.ndenumerate(data):
            if val < threshold:
                mask[i, j] = False
        
        # Determine the proper offset in pixels based on the image
        # dimensions.
        sfx = self.dims_in.read_data[0] / (self.lum_in.read_data.shape[1] - 1)
        sfy = self.dims_in.read_data[1] / (self.lum_in.read_data.shape[0] - 1)
        px_offset = int(self.offset / np.average((sfx, sfy)) * 2**0.5 * 0.5)
        
        # Iterate over the mask array and detect edge points by taking
        # a sample subset of the array about the test point and determining
        # if 40-60% of the data is below the threshold.
        for (i, j), val in np.ndenumerate(mask):
            if val:
                if (count-1) < i < (data.shape[0]-count) and \
                        (count-1) < j < (data.shape[1]-count):
                    test_arr = mask[i-count : i+count+1,
                                    j-count : j+count+1]
                    test_edge = len(
                        np.where(test_arr)[0]) / test_size
                    if 0.4 < test_edge < 0.6:
                        edge_list.append((i, j))
        
        # Set points within an offset radius of each edge point to False 
        for x, y in edge_list:
            limits = [[x-px_offset, x+px_offset+1],
                      [y-px_offset, y+px_offset+1]]
            for i in range(0, 2):
                if limits[i][0] < 0: 
                    limits[i][0] = 0
                if limits[i][1] > mask.shape[i]-1:
                    limits[i][1] = mask.shape[i]-1
               
            mask[limits[0][0]:limits[0][1], 
                 limits[1][0]:limits[1][1]].fill(False)
        
#         print(mask.shape)
        self.outputs[0].set(mask)     

class Uniformity(CalcProcess):
    """
    Take an array of luminance data and the min/max dimensional values
    of the array and calculate the uniformity by fitting a plane at each
    point, using a set of points within a square of width (2 * dx + 1)
    centered about the point.
    """
    
    gui_commands = [
        ("SelectNameLabelFrame",
         ("lum_in", "out_name", "to_db"),
         ("Input:", "Output Name:", "Luminance Data", 400, (60, 100)),
         True),
        ("ComboboxFrame",
         "mask_in",
         ("Mask Array:", 200, 75), True),
        ("ComboboxFrame",
         "dims",
         ("Dimensions [mm]:", 200, 75), True),
        ("SpboxFrame", "dx", ("Smoothing", list(range(1,11)), 150, 75)),
        ("SpboxFrame", "reduction", 
         ("Reduction", list(range(1,20)), 150, 75))]
    
    def __init__(self, out_name, to_db, lum_in, mask_in, dims, dx, reduction):
        
        self.name = "Uniformity"
        self.lum_in = lum_in
        self.mask_in = mask_in
        self.dims = dims
        self.out_name = out_name
        self.to_db = to_db
        self.dx = dx
        self.reduction = reduction
        
        CalcProcess.__init__(
            self, 
            [lum_in.calc, dims.calc, mask_in.calc])
        self.inputs = [lum_in.name, mask_in.name, dims.name]
        self.outputs.append(
            DataObject(self.out_name, np.array([]), self, self.to_db))
        
    def check(self):
        return None
        
    def run(self):
        
        dx = int(self.dx)
        r = int(self.reduction)
        
        # Scale factors in the x,y directions
        sfx = self.dims.read_data[0] / (self.lum_in.read_data.shape[1] - 1)
        sfy = self.dims.read_data[1] / (self.lum_in.read_data.shape[0] - 1)
        
        # Get proper shapes (accounting for loss of self.dx to each side)
        mask = self.mask_in.read_data[dx:-dx, dx:-dx]
        uni_out = np.full(mask.shape, 0)
        
        for (i, j), _ in np.ndenumerate(uni_out):
            
            # Only compute uniformity at unmasked points
            if mask[i, j]:
                
                # Only compute uniformity at every r-th point
                if i % r == 0 and j % r == 0:
                    sample_arr = self.lum_in.read_data[
                        (i):(i + 2*dx + 1),
                        (j):(j + 2*dx + 1)]
                    pt_list = []
                    
                    # Compute best fit plane
                    for (u, v), sample in np.ndenumerate(sample_arr):
                        pt_list.append([u * sfy, v * sfx, sample])
                    pt_list = np.asarray(pt_list)
                    x, y, z = pt_list[:, 0], pt_list[:, 1], pt_list[:, 2]
                     
                    A = np.c_[x, y, np.ones(pt_list.shape[0])]
                         
                    C, _, _, _ = np.linalg.lstsq(A, z, rcond=None)
                    
                    # Spatial component of plane normal vector
                    n_s = ((C[0]**2 + C[1]**2) / (C[0]**2 + C[1]**2 + 1)) ** 0.5
                    
                    # Value component of plane normal vector
                    n_v = (1 / (C[0]**2 + C[1]**2 + 1)) ** 0.5
                    
                    # The uniformity is the slope of the surface
                    uni_out[i, j] = n_s / n_v
                else:
                    uni_out[i, j] = uni_out[i - i % r, j - j % r]
         
        # Apply mask to output uniformity heat map
        uni_out = np.multiply(uni_out, mask)
         
        self.outputs[0].set(uni_out)
        
class HeatmapStats(CalcProcess):
    """
    Take an array of heatmap data and output a set of standard statistical
    parameters for the heatmap, as well as a histogram of the data.
    """
    gui_commands = [
        ("SelectNameLabelFrame",
         ("data_in", 
          ("out_name_mean", "out_name_max", "out_name_median",
            "out_name_75", "out_name_95", "out_name_99", "out_name_hist"), 
          ("mean_to_db", "max_to_db", "median_to_db", "p75_to_db", "p95_to_db",
           "p99_to_db", "hist_to_db")),
         ("Input:", 
          ("Mean Name:", "Max Name:", "Median Name:", "75% Name:",
           "95% Name:", "99% Name:", "Histogram Name:"),
          "Heatmap Data", 420, (50, 100)), True),
        ("SpboxFrame", "n_bins",
         ("Histogram Bins", list(range(10,200)), 200, 120)),
        ("CheckEntryFrame", "log_hist", "Use Logarithmic Bins for Histogram?")]
    
    def __init__(self, data_in, out_name_mean, out_name_max, out_name_median,
                 out_name_75, out_name_95, out_name_99, out_name_hist, 
                 mean_to_db, max_to_db, median_to_db, p75_to_db, p95_to_db,
                 p99_to_db, hist_to_db, n_bins, log_hist):
        
        self.name = "Heatmap Statistics"
        self.data_in = data_in
        self.out_name_mean = out_name_mean
        self.out_name_max = out_name_max
        self.out_name_median = out_name_median
        self.out_name_75 = out_name_75
        self.out_name_95 = out_name_95
        self.out_name_99 = out_name_99
        self.out_name_hist = out_name_hist
        self.mean_to_db = mean_to_db
        self.max_to_db = max_to_db
        self.median_to_db = median_to_db
        self.p75_to_db = p75_to_db
        self.p95_to_db = p95_to_db
        self.p99_to_db = p99_to_db
        self.hist_to_db = hist_to_db
        self.n_bins = n_bins
        self.log_hist = log_hist
        
        CalcProcess.__init__(self, [data_in.calc])
        
        self.inputs.append(data_in.name)
        self.outputs.extend([
            DataObject(out_name_mean, None, self, mean_to_db),
            DataObject(out_name_max, None, self, max_to_db),
            DataObject(out_name_median, None, self, median_to_db),
            DataObject(out_name_75, None, self, p75_to_db),
            DataObject(out_name_95, None, self, p95_to_db),
            DataObject(out_name_99, None, self, p99_to_db),
            DataObject(out_name_hist, np.array([]), self, hist_to_db)])
    
    def run(self):
        
        data_in = self.data_in.read_data
        
        # Sample background noise data around edge of the input data
        noise_sample = np.concatenate((
            data_in[0,:], 
            data_in[-1,:],
            data_in[:,0][1:-1],
            data_in[:,-1][1:-1]))
        noise_threshold = np.average(noise_sample) + 12 * np.std(noise_sample)
        if noise_threshold < 0.1:
            noise_threshold = 1
        
        data_filtered = data_in[data_in > noise_threshold]
        
        try:
            data_mean = float(np.mean(data_filtered))
            data_max = float(np.max(data_filtered))
            data_median = float(np.percentile(data_filtered, 50))
            data_p75 = float(np.percentile(data_filtered, 75))
            data_p95 = float(np.percentile(data_filtered, 95))
            data_p99 = float(np.percentile(data_filtered, 99))
        except ValueError:  # Handle completely masked data
            data_mean = 0
            data_max = 0
            data_median = 0
            data_p75 = 0
            data_p95 = 0
            data_p99 = 0
        
        # Generate histogram
        if self.log_hist:
            n, bins = np.histogram(
                data_in, 
                np.logspace(
                    np.log10(noise_threshold), 
                    np.log10(np.max(data_in)),
                    self.n_bins), (noise_threshold, data_in.max()))
        else:
            n, bins = np.histogram(
                data_in, int(self.n_bins), (noise_threshold, data_in.max()))
        
        hist_arr = np.array(list(zip(bins, n)))
        
        self.outputs[0].set(data_mean)
        self.outputs[1].set(data_max)
        self.outputs[2].set(data_median)
        self.outputs[3].set(data_p75)
        self.outputs[4].set(data_p95)
        self.outputs[5].set(data_p99)
        self.outputs[6].set(hist_arr)

class LightLeakage(CalcProcess):
    """
    Apply a mask to an array of luminance data to remove edges where
    light leakage might occur. Output the calculated light leakage
    (i.e. ratio of unmasked max to masked max), the unmasked max, and
    masked luminance array.
    """
    gui_commands = [
        ("SelectNameLabelFrame",
         (("data_in", "mask_in"), 
          ("out_name_masked", "out_name_leak", "out_name_peak"), 
          ("masked_to_db", "leak_to_db", "peak_to_db")),
         (("Luminance Data:", "Edge Mask:"), 
          ("Masked Luminance Name:", "Light Leakage Name:", "Masked Max Name:"),
          "Data Input", 500, (100, 150)), True)]
    
    def __init__(self, data_in, mask_in, out_name_masked, out_name_leak,
                 out_name_peak, masked_to_db, leak_to_db, peak_to_db):
        
        self.name = "Light Leakage"
        self.data_in = data_in
        self.mask_in = mask_in
        self.out_name_masked = out_name_masked
        self.out_name_leak = out_name_leak
        self.out_name_peak = out_name_peak
        self.masked_to_db = masked_to_db
        self.leak_to_db = leak_to_db
        self.peak_to_db = peak_to_db
        
        CalcProcess.__init__(self, [data_in.calc, mask_in.calc])
        
        self.inputs = [data_in.name, mask_in.name]
        self.outputs.extend([
            DataObject(out_name_masked, np.array([]), self, masked_to_db),
            DataObject(out_name_leak, None, self, leak_to_db),
            DataObject(out_name_peak, None, self, peak_to_db)])
    
    def run(self):
        
        lum_masked = np.multiply(self.data_in.read_data, self.mask_in.read_data)
        peak_masked = lum_masked.max()
        leakage = "{0:.00%}".format(self.data_in.read_data.max() / peak_masked)
        
        self.outputs[0].set(lum_masked)
        self.outputs[1].set(leakage)
        self.outputs[2].set(float(peak_masked))
        
class ChromStats(CalcProcess):
    """
    Apply a mask to arrays of chromaticity coordinate data and generate
    relevant statistics and a 2D histogram of the data. 
    """
    gui_commands = [
        ("SelectNameLabelFrame",
         (("c_x_in", "c_y_in", "mask_in"), 
          ("out_name_xmean", "out_name_xmode", "out_name_ymean",
           "out_name_ymode", "out_name_xbins", "out_name_ybins", 
           "out_name_hist"), 
          ("xmean_to_db", "xmode_to_db", "ymean_to_db", "ymode_to_db",
           "xbins_to_db", "ybins_to_db", "hist_to_db")),
         (("Chrom. X Data:", "Chrom. Y Data:", "Edge Mask:"), 
          ("X Mean Name:", "X Mode Name:", "Y Mean Name:", "Y Mode Name:",
           "X Hist. Bins Name:", "Y Hist. Bins Name:", "Histogram Name:"),
          "Data Input", 500, (100, 100)), True),
        ("SpboxFrame", "n_bins",
         ("Histogram Bins", list(range(10,200)), 200, 120))]
    
    def __init__(self, c_x_in, c_y_in, mask_in, out_name_xmean, out_name_xmode,
                 out_name_ymean, out_name_ymode, out_name_xbins, out_name_ybins, 
                 out_name_hist, xmean_to_db, xmode_to_db, ymean_to_db, 
                 ymode_to_db, xbins_to_db, ybins_to_db, hist_to_db, n_bins):
        
        self.name = "Chromaticity Statistics"
        self.c_x_in = c_x_in
        self.c_y_in = c_y_in
        self.mask_in = mask_in
        self.out_name_xmean = out_name_xmean
        self.out_name_xmode = out_name_xmode
        self.out_name_ymean = out_name_ymean
        self.out_name_ymode = out_name_ymode
        self.out_name_xbins = out_name_xbins
        self.out_name_ybins = out_name_ybins
        self.out_name_hist = out_name_hist
        self.xmean_to_db = xmean_to_db
        self.xmode_to_db = xmode_to_db
        self.ymean_to_db = ymean_to_db
        self.ymode_to_db = ymode_to_db
        self.xbins_to_db = xbins_to_db
        self.ybins_to_db = ybins_to_db
        self.hist_to_db = hist_to_db
        self.n_bins = n_bins
        
        CalcProcess.__init__(self, [c_x_in.calc, c_y_in.calc, mask_in.calc])
        
        self.inputs = [c_x_in.name, c_y_in.name, mask_in.name]
        self.outputs.extend([
            DataObject(out_name_xmean, None, self, xmean_to_db),
            DataObject(out_name_xmode, None, self, xmode_to_db),
            DataObject(out_name_ymean, None, self, ymean_to_db),
            DataObject(out_name_ymode, None, self, ymode_to_db),
            DataObject(out_name_xbins, np.array([]), self, xbins_to_db),
            DataObject(out_name_ybins, np.array([]), self, ybins_to_db),
            DataObject(out_name_hist, np.array([]), self, hist_to_db)])
            
    def run(self):
        
        self.n_bins = int(self.n_bins)
        
        # Apply the mask to the chromaticity data
        c_x = np.ndarray.flatten(np.multiply(
            self.c_x_in.read_data, self.mask_in.read_data))
#         c_x_masked = np.ma.masked_less_equal(c_x, 0)
        c_y = np.ndarray.flatten(np.multiply(
            self.c_y_in.read_data, self.mask_in.read_data))
#         c_y_masked = np.ma.masked_less_equal(c_y, 0)
        
        # Filter out values that must be invalid based on out of
        # range coordinates (i.e. outside visible region of CIE 1931)
        c_x_filtered = c_x[c_x > 0.0036]
        c_x_filtered = c_x_filtered[c_x_filtered < 0.735]
        c_y_filtered = c_y[c_y > 0.0048]
        c_y_filtered = c_y_filtered[c_y_filtered < 0.835]
        
        self.outputs[0].set(float(np.mean(c_x_filtered)))
        self.outputs[2].set(float(np.mean(c_y_filtered)))
        
        # Expel outliers
        xmin = np.percentile(c_x_filtered, 1)
        xmax = np.percentile(c_x_filtered, 99)
        ymin = np.percentile(c_y_filtered, 1)
        ymax = np.percentile(c_y_filtered, 99)
        
        # Generate the histogram and calculate the mode of each coordinate
        n, xbins, ybins = np.histogram2d(
            c_x, c_y, self.n_bins, [[xmin-0.01, xmax+0.01], 
                                    [ymin-0.01, ymax+0.01]])
        n = n.T
        
        nx_max = np.argmax(np.sum(n, axis=1))
        ny_max = np.argmax(np.sum(n, axis=0))
        
        xmode = np.mean((xbins[nx_max], xbins[nx_max+1]))
        ymode = np.mean((ybins[ny_max], ybins[ny_max+1]))
        
        self.outputs[1].set(float(xmode))
        self.outputs[3].set(float(ymode))
        self.outputs[4].set(xbins)
        self.outputs[5].set(ybins)
        self.outputs[6].set(n)
        
class DominantWL(CalcProcess):
    """
    Apply a mask to arrays of chromaticity coordinate data and resolve
    the coordinates at each point to a dominant wavelength (or purple hue).
    """
    gui_commands = [
        ("SelectNameLabelFrame",
         (("c_x_in", "c_y_in", "mask_in"), 
          ("out_name_wlmean", "out_name_wlmode", "out_name_phmean",
           "out_name_phmode", "out_name_wlhist", "out_name_phhist",
           "out_name_wlmap"), 
          ("wlmean_to_db", "wlmode_to_db", "phmean_to_db", "phmode_to_db",
           "wlhist_to_db", "phhist_to_db", "wlmap_to_db")),
         (("Chrom. X Data:", "Chrom. Y Data:", "Edge Mask:"), 
          ("WL Mean Name:", "WL Mode Name:", "PH Mean Name:", "PH Mode Name:",
           "WL Hist. Name:", "PH Hist. Name:", "WL Map Name:"),
          "Data Input", 500, (100, 120)), True),
        ("SpboxFrame", "reduction", 
         ("Reduction", list(range(1,20)), 150, 75))]
    
    def __init__(self, c_x_in, c_y_in, mask_in, out_name_wlmean, 
                 out_name_wlmode, out_name_phmean, out_name_phmode,
                 out_name_wlhist, out_name_phhist, out_name_wlmap, 
                 wlmean_to_db, wlmode_to_db, phmean_to_db, phmode_to_db, 
                 wlhist_to_db, phhist_to_db, wlmap_to_db, reduction):
        
        self.name = "Dominant Wavelength"
        self.c_x_in = c_x_in
        self.c_y_in = c_y_in
        self.mask_in = mask_in
        self.out_name_wlmean = out_name_wlmean
        self.out_name_wlmode = out_name_wlmode
        self.out_name_phmean = out_name_phmean
        self.out_name_phmode = out_name_phmode
        self.out_name_wlhist = out_name_wlhist
        self.out_name_phhist = out_name_phhist
        self.out_name_wlmap = out_name_wlmap
        self.wlmean_to_db = wlmean_to_db
        self.wlmode_to_db = wlmode_to_db
        self.phmean_to_db = phmean_to_db
        self.phmode_to_db = phmode_to_db
        self.wlhist_to_db = wlhist_to_db
        self.phhist_to_db = phhist_to_db
        self.wlmap_to_db = wlmap_to_db
        self.reduction = reduction
        
        CalcProcess.__init__(self, [c_x_in.calc, c_y_in.calc, mask_in.calc])
        
        self.inputs = [c_x_in.name, c_y_in.name, mask_in.name]
        self.outputs.extend([
            DataObject(out_name_wlmean, None, self, wlmean_to_db),
            DataObject(out_name_wlmode, None, self, wlmode_to_db),
            DataObject(out_name_phmean, None, self, phmean_to_db),
            DataObject(out_name_phmode, None, self, phmode_to_db),
            DataObject(out_name_wlhist, np.array([]), self, wlhist_to_db),
            DataObject(out_name_phhist, np.array([]), self, phhist_to_db),
            DataObject(out_name_wlmap, np.array([]), self, wlmap_to_db)])
    
    def run(self):
        
        r = int(self.reduction)
        c_x = self.c_x_in.read_data
        c_y = self.c_y_in.read_data
        mask = self.mask_in.read_data
        wlmap = np.full(c_x.shape, 0.)
        
        # Standard D65 illuminant white point
        white_pt = (0.31271, 0.32902)
        
        # If data is to be reduced, go through unmasked region of the
        # data set and average chromaticity coordinates by reduction bin
        if r > 1:
            for (i, j), _ in np.ndenumerate(c_x):
                if mask[i, j]:
                    if i % r == 0 and j % r == 0:
                        c_x[i, j] = np.mean(c_x[i : i+r-1, j : j+r-1])
                        c_y[i, j] = np.mean(c_y[i : i+r-1, j : j+r-1])
        
        # Wavelength keys for first pass rough approx of spectral locus
        first_pass = [360, 500, 510, 520, 540, 560, 830]
        
        for (i, j), _ in np.ndenumerate(c_x[:-r, :-r]):
            if mask[i : i+r, j : j+r].any():
                if i % r == 0 and j % r == 0:
                    meas_pt = (c_x[i, j], c_y[i, j])
                    int_pt = None
                    k = -2
                    
                    # Conduct first pass
                    while int_pt == None:
                        k += 1
                        int_pt = self.check_int(
                            chrom_dict[first_pass[k]],
                            chrom_dict[first_pass[k+1]],
                            white_pt, meas_pt)
                    
                    # Handle intersection point on line of purples
                    if k == -1:
                        val = self.partial_int(
                            meas_pt, chrom_dict[360], chrom_dict[830])
                        wlmap[i : i+r, j : j+r] = val
                    
                    else:
                        interval = [first_pass[k], first_pass[k+1]]
                        
                        # Home in on the intersection point with the
                        # spectral locus
                        while interval[1]-interval[0] > 1:
                            
                            int_pt = None
                            k = -1
                            next_pass = [interval[0],
                                         int(np.mean(interval)),
                                         interval[1]]
                            
                            while int_pt == None:
                                k += 1
                                int_pt = self.check_int(
                                    chrom_dict[next_pass[k]],
                                    chrom_dict[next_pass[k+1]],
                                    white_pt, meas_pt)
                            
                            interval = [next_pass[k], next_pass[k+1]]
                        
                        # Set the wavelength value as the closest
                        # integer wavelength value to the intersection
                        val = self.partial_int(
                            meas_pt, chrom_dict[interval[0]], 
                            chrom_dict[interval[1]])
                        
                        if val <= 0.5:
                            val = interval[0]
                        else:
                            val = interval[1]
                        
                        wlmap[i : i+r, j : j+r] = val
        
        wlmap = np.multiply(wlmap, mask)
        
        # Sift out points where a valid wavelength was found or where
        # a purple hue was found
        wlmap_filter_wl = wlmap[wlmap >= 360]
        wlmap_filter_ph = wlmap[wlmap < 360]
        wlmap_filter_ph = wlmap_filter_ph[wlmap_filter_ph > 0]
        
        if len(wlmap_filter_wl) > 0:
            n_wl, bins_wl = np.histogram(wlmap_filter_wl, 94, (360, 830))
            wl_mean = np.mean(wlmap_filter_wl)
            wl_mode = bins_wl[np.argmax(n_wl)]
        else:
            n_wl, bins_wl = np.full(94, 0.0001), np.linspace(360, 830, 95)
            wl_mean = 0
            wl_mode = 0
        
        if len(wlmap_filter_ph) > 0:
            n_ph, bins_ph = np.histogram(wlmap_filter_ph, 25, (0, 1))
            ph_mean = np.mean(wlmap_filter_ph)
            ph_mode = bins_wl[np.argmax(n_ph)]
        else:
            n_ph, bins_ph = np.full(25, 0.0001), np.linspace(0, 1, 26)
            ph_mean = 0
            ph_mode = 0
        
        # To a large value that will be converted to gray in the heatmap
        for (i, j), _ in np.ndenumerate(wlmap):
            if 0 < wlmap[i, j] <= 1:
                wlmap[i, j] = 10000
        
        wl_hist_arr = np.array(list(zip(bins_wl, n_wl)))
        ph_hist_arr = np.array(list(zip(bins_ph, n_ph)))
        
        self.outputs[0].set(float(wl_mean))
        self.outputs[1].set(float(wl_mode))
        self.outputs[2].set(float(ph_mean))
        self.outputs[3].set(float(ph_mode))
        self.outputs[4].set(wl_hist_arr)
        self.outputs[5].set(ph_hist_arr)
        self.outputs[6].set(wlmap)
                
    def check_int(self, seg1, seg2, wp, meas):
        
        # Check if the ray emanating from wp to meas intersects with
        # the line segment defined by seg1 and seg2
        m_seg = (seg2[1] - seg1[1]) / (seg2[0] - seg1[0])
        b_seg = seg1[1] - seg1[0] * m_seg
        
        m_ray = (meas[1] - wp[1]) / (meas[0] - wp[0])
        b_ray = wp[1] - wp[0] * m_ray
        
        int_pt = ((b_ray - b_seg) / (m_seg - m_ray),
                  m_seg * ((b_ray - b_seg) / (m_seg - m_ray)) + b_seg)
        
        # Check if intersection point is in the direction of the ray
        if all(np.signbit(np.subtract(meas, wp)) == \
               np.signbit(np.subtract(int_pt, wp))):
            
            # Check if the intersection point falls between the two line
            # segment points
            if all(np.signbit(np.subtract(int_pt, seg1)) != \
                   np.signbit(np.subtract(int_pt, seg2))):
                return int_pt
        
        return None
    
    def partial_int(self, meas, pt1, pt2):
        
        # Point meas falls on the line segment between pt1 and pt2.
        # Return the ratio of meas-pt1 to pt2-pt1.
        return np.linalg.norm(np.subtract(meas, pt1)) \
            / np.linalg.norm(np.subtract(pt2, pt1))

# CIE 1931 chromaticity spectral locus data
chrom_dict = {360: (0.175560231755724, 0.00529383701144858),
              361: (0.175482527710407, 0.00528633910591523),
              362: (0.175400022356684, 0.00527864204310934),
              363: (0.175317049458602, 0.00527096879423463),
              364: (0.175236739463886, 0.00526349392275481),
              365: (0.175161218506262, 0.00525634591510605),
              366: (0.175087794161125, 0.0052468445276602),
              367: (0.175014938867913, 0.00523557032866828),
              368: (0.174945189438668, 0.00522615691108036),
              369: (0.174880124778842, 0.0052207849401792),
              370: (0.174820607679635, 0.00522060093793847),
              371: (0.174770252213918, 0.00522866721672108),
              372: (0.174722036673711, 0.00523752017723635),
              373: (0.174665367950954, 0.00523616066324846),
              374: (0.174595050265963, 0.00521832225253951),
              375: (0.17450972086916, 0.00518163977014415),
              376: (0.174409249351858, 0.00512676089768082),
              377: (0.174308458223786, 0.00506759252024135),
              378: (0.174221772058161, 0.0050170315362969),
              379: (0.174155594353273, 0.00498144491089279),
              380: (0.174112234426342, 0.00496372598145272),
              381: (0.17408830716741, 0.00496360006529369),
              382: (0.174072590901536, 0.00497254261822802),
              383: (0.174057024292786, 0.00498203613909543),
              384: (0.17403627060996, 0.00498596142862248),
              385: (0.174007917515889, 0.00498054862299504),
              386: (0.173971929754687, 0.00496408309597096),
              387: (0.173931678596305, 0.0049434066494304),
              388: (0.1738890357771, 0.00492604851075011),
              389: (0.173845256167111, 0.00491609307090683),
              390: (0.173800772620828, 0.00491541190537341),
              391: (0.173754438047173, 0.00492485369535323),
              392: (0.17370535274905, 0.00493709837109517),
              393: (0.173655189400453, 0.00494379098332086),
              394: (0.173606018216907, 0.00493989527110925),
              395: (0.173559906527214, 0.00492320257730789),
              396: (0.173514449742224, 0.00489544671312358),
              397: (0.173468498200431, 0.00486457913883596),
              398: (0.173423666225833, 0.00483631212221056),
              399: (0.173379996016857, 0.00481333832384587),
              400: (0.173336865480781, 0.00479674344726689),
              401: (0.173291285658761, 0.00478584564814538),
              402: (0.173237920453112, 0.00477888793221686),
              403: (0.173174238776235, 0.00477513079983524),
              404: (0.173101012208515, 0.00477403067449075),
              405: (0.173020965455495, 0.00477505036185929),
              406: (0.172934256850859, 0.00478114717178147),
              407: (0.172842756135349, 0.00479079294906705),
              408: (0.172751152603347, 0.00479876209926314),
              409: (0.172662105581222, 0.00480208435632195),
              410: (0.172576550848802, 0.00479930191972077),
              411: (0.172489477381802, 0.0047952543644012),
              412: (0.172395603384173, 0.00479611858893491),
              413: (0.172296001755019, 0.00480262947347127),
              414: (0.172192360361959, 0.0048148852140205),
              415: (0.172086630755248, 0.00483252421803995),
              416: (0.171982445938222, 0.00485501016856446),
              417: (0.171871019445674, 0.00488853192151211),
              418: (0.171741213705737, 0.00493933245661687),
              419: (0.171587239364847, 0.00501034420683924),
              420: (0.171407433863109, 0.00510217097374933),
              421: (0.171206113461594, 0.00521125777669814),
              422: (0.170992574221804, 0.00533390776201582),
              423: (0.170770596367909, 0.00547012124749784),
              424: (0.170540661923529, 0.00562096993347462),
              425: (0.170300988779736, 0.00578850499647099),
              426: (0.170050158668149, 0.00597389510789107),
              427: (0.16978586875087, 0.00617680748815949),
              428: (0.169504602532254, 0.00639803690687803),
              429: (0.169202921712127, 0.00663870591838744),
              430: (0.168877520670989, 0.00690024388793052),
              431: (0.168524660344249, 0.00718404388802375),
              432: (0.168146145461531, 0.00749067966632363),
              433: (0.167746219826537, 0.00782081848842158),
              434: (0.167328325744596, 0.00817539967500124),
              435: (0.16689529035208, 0.00855560636081898),
              436: (0.166446327135003, 0.0089644004177575),
              437: (0.165976758230656, 0.00940171622686875),
              438: (0.165483299011466, 0.00986468097234593),
              439: (0.164962663720259, 0.0103507435414824),
              440: (0.164411756375275, 0.0108575582767639),
              441: (0.163828432761608, 0.0113848656159641),
              442: (0.163209895954422, 0.0119373858145677),
              443: (0.162552139506799, 0.0125200299175854),
              444: (0.161851438065089, 0.013137307095434),
              445: (0.161104579580275, 0.0137933588217324),
              446: (0.160309595019389, 0.0144913781663337),
              447: (0.159465945758018, 0.0152320646437253),
              448: (0.158573111075907, 0.0160151564155888),
              449: (0.157631165578262, 0.0168398709715094),
              450: (0.156640932577307, 0.0177048049908913),
              451: (0.155605095582748, 0.0186086065240072),
              452: (0.154524612494681, 0.0195556978045396),
              453: (0.153397229336432, 0.0205537335298569),
              454: (0.152219236228253, 0.0216117110209021),
              455: (0.150985408375971, 0.022740193291643),
              456: (0.149690564758713, 0.0239503301957584),
              457: (0.148336817067949, 0.0252473984317283),
              458: (0.146928226501376, 0.0266351858576878),
              459: (0.145468371778522, 0.0281184333297045),
              460: (0.143960396039604, 0.0297029702970297),
              461: (0.142405090190101, 0.0313935839862295),
              462: (0.14079564666459, 0.03321315460626),
              463: (0.139120682426571, 0.0352005728268017),
              464: (0.137363757935118, 0.0374030904436341),
              465: (0.135502671199611, 0.0398791214721278),
              466: (0.133509340955908, 0.0426923900105262),
              467: (0.131370635235575, 0.0458759752225473),
              468: (0.129085786557187, 0.0494498106597349),
              469: (0.126662156977009, 0.0534259197730497),
              470: (0.124118476727786, 0.0578025133737405),
              471: (0.121468583913083, 0.0625876720665533),
              472: (0.118701276452039, 0.0678304435323486),
              473: (0.115807358768397, 0.0735807079728414),
              474: (0.11277605484761, 0.0798958228959609),
              475: (0.10959432361561, 0.0868425111830942),
              476: (0.106260735317928, 0.0944860722037205),
              477: (0.10277586294651, 0.102863738818152),
              478: (0.0991275999016733, 0.112007033037195),
              479: (0.0953040562149913, 0.121944863254658),
              480: (0.0912935070022712, 0.13270204248699),
              481: (0.0870824317270964, 0.144316582680233),
              482: (0.082679534481971, 0.15686595807724),
              483: (0.0781159857333012, 0.170420486476505),
              484: (0.0734372599047498, 0.18503188052712),
              485: (0.0687059212910555, 0.200723217728102),
              486: (0.0639930236869067, 0.217467605405061),
              487: (0.0593158279806231, 0.235253740241245),
              488: (0.0546665228761952, 0.254095590747025),
              489: (0.0500314970581197, 0.274001803219802),
              490: (0.0453907346747777, 0.294975964606287),
              491: (0.0407573153360254, 0.316981080839994),
              492: (0.0361951091539399, 0.339899934413942),
              493: (0.0317564703789208, 0.363597693246343),
              494: (0.0274941905347843, 0.387921328280829),
              495: (0.0234599425470795, 0.412703479093521),
              496: (0.0197046363029537, 0.437755888652074),
              497: (0.0162684712672383, 0.462954507988606),
              498: (0.0131830411530808, 0.48820706841228),
              499: (0.0104757006831256, 0.513404245160212),
              500: (0.00816802800466744, 0.538423070511752),
              501: (0.00628485157264002, 0.563068456321616),
              502: (0.00487542999269079, 0.587116438044602),
              503: (0.00398242535235287, 0.610447497638674),
              504: (0.00363638422545277, 0.633011382750804),
              505: (0.00385852090032154, 0.654823151125402),
              506: (0.00464571323255553, 0.675898458599253),
              507: (0.00601091307169603, 0.696120061336206),
              508: (0.00798839582865335, 0.715341516255831),
              509: (0.010603290554259, 0.733412942651556),
              510: (0.0138702460850112, 0.750186428038777),
              511: (0.017766124205863, 0.765612154434196),
              512: (0.0222442056947439, 0.779629923200771),
              513: (0.02727326242017, 0.792103502831263),
              514: (0.0328203575222175, 0.80292567298964),
              515: (0.0388518024032043, 0.812016021361816),
              516: (0.0453279848294139, 0.819390800456081),
              517: (0.0521766909052169, 0.825163542582536),
              518: (0.0593255333519871, 0.829425776296551),
              519: (0.0667158860270346, 0.832273739283868),
              520: (0.074302424773375, 0.833803091340228),
              521: (0.0820533952358065, 0.834090314504944),
              522: (0.0899417395853361, 0.833288918895958),
              523: (0.0979397501105561, 0.831592666498741),
              524: (0.106021107332241, 0.829178186631099),
              525: (0.11416071960668, 0.826206959781189),
              526: (0.122347367033701, 0.822770399563869),
              527: (0.130545668138394, 0.818927852909404),
              528: (0.138702349214235, 0.814774382594947),
              529: (0.146773215738364, 0.810394606547811),
              530: (0.154722061215713, 0.805863545425649),
              531: (0.162535424655456, 0.801238480413611),
              532: (0.170237195478923, 0.796518542245412),
              533: (0.177849528011742, 0.791686579059916),
              534: (0.185390757399363, 0.786727772820681),
              535: (0.192876097877721, 0.781629216363077),
              536: (0.200308798144942, 0.77639941605062),
              537: (0.207689989666574, 0.771054798660324),
              538: (0.215029550005768, 0.765595096060611),
              539: (0.222336603758204, 0.760019999740836),
              540: (0.22961967264964, 0.754329089902744),
              541: (0.236884720598308, 0.748524465174775),
              542: (0.244132556473824, 0.742613991681373),
              543: (0.251363408870738, 0.736605581362445),
              544: (0.258577508455251, 0.730506601909747),
              545: (0.265775084971184, 0.724323924929806),
              546: (0.27295760351093, 0.71806218641679),
              547: (0.280128942481592, 0.711724734569193),
              548: (0.287292409080259, 0.705316273888283),
              549: (0.294450280894396, 0.698842022022381),
              550: (0.301603799395751, 0.692307762371574),
              551: (0.308759923092657, 0.68571206060674),
              552: (0.315914394448992, 0.67906347999093),
              553: (0.323066265382129, 0.672367397968749),
              554: (0.330215545356897, 0.665628025417149),
              555: (0.337363332850857, 0.658848290139688),
              556: (0.344513198355454, 0.652028209217844),
              557: (0.35166441129682, 0.645172174245398),
              558: (0.358813686684303, 0.638287336537753),
              559: (0.365959357349119, 0.631379080899849),
              560: (0.373101543868457, 0.624450859796661),
              561: (0.380243835464065, 0.617502152173705),
              562: (0.387378977958644, 0.610541802455016),
              563: (0.394506548796889, 0.603571336791597),
              564: (0.401625918831181, 0.596592421962562),
              565: (0.408736255706423, 0.589606868859531),
              566: (0.415835774705559, 0.582617968056976),
              567: (0.422920926709796, 0.575630688323188),
              568: (0.429988626512438, 0.568648891270804),
              569: (0.437036422593891, 0.561675774049367),
              570: (0.444062463582333, 0.554713902808531),
              571: (0.451064940950767, 0.547766044129445),
              572: (0.458040665647423, 0.540836629164402),
              573: (0.464986332977633, 0.533930053056831),
              574: (0.471898743899668, 0.527050569219262),
              575: (0.478774791157584, 0.520202307211456),
              576: (0.485611587052091, 0.51338866096156),
              577: (0.492404982334296, 0.506614924420926),
              578: (0.499150668334298, 0.499887340438306),
              579: (0.505845283794021, 0.493211178107541),
              580: (0.512486366781797, 0.486590788060857),
              581: (0.519072510400636, 0.480028612176447),
              582: (0.525600488985451, 0.473527373975529),
              583: (0.53206559916124, 0.467091363703909),
              584: (0.538462761902554, 0.460725253840842),
              585: (0.544786505594834, 0.454434114568836),
              586: (0.551031050212292, 0.448224502909975),
              587: (0.557192906096034, 0.44209913948419),
              588: (0.563269312373157, 0.436058061736674),
              589: (0.569256824124726, 0.430101973605084),
              590: (0.575151311365165, 0.424232234924905),
              591: (0.580952605160923, 0.418446879816537),
              592: (0.586650186890891, 0.412758421192096),
              593: (0.592224800070941, 0.407189528585467),
              594: (0.597658162105241, 0.40176193497228),
              595: (0.602932785575716, 0.396496633572977),
              596: (0.608035111132285, 0.391409151707708),
              597: (0.612976999570812, 0.386486157331698),
              598: (0.617778725585283, 0.381705756828504),
              599: (0.622459295078623, 0.377047286380739),
              600: (0.627036599763872, 0.372491145218418),
              601: (0.63152094286026, 0.368026010821791),
              602: (0.635899819576266, 0.363665402433267),
              603: (0.640156159547881, 0.359427724303784),
              604: (0.644272960657274, 0.355331369771593),
              605: (0.648233106013639, 0.351394916305022),
              606: (0.65202823571793, 0.347627960748423),
              607: (0.655669179249501, 0.344018294844416),
              608: (0.659166134692712, 0.340553225412233),
              609: (0.662528222053688, 0.337220992607213),
              610: (0.665763576238097, 0.334010651154761),
              611: (0.668874143663558, 0.330918553002487),
              612: (0.671858667147589, 0.327947074299904),
              613: (0.674719511111516, 0.325095182004255),
              614: (0.677458888275166, 0.322362076688633),
              615: (0.680078849721707, 0.319747217068646),
              616: (0.68258157418701, 0.317248705962303),
              617: (0.684970601448709, 0.314862815015325),
              618: (0.687250454556694, 0.312585963995597),
              619: (0.689426303027996, 0.310414011285913),
              620: (0.691503972961702, 0.308342260556656),
              621: (0.693489634972634, 0.306365690817556),
              622: (0.695388638101952, 0.304478555199648),
              623: (0.697205569778691, 0.302675072703968),
              624: (0.698943910385795, 0.300950424978996),
              625: (0.700606060606061, 0.299300699300699),
              626: (0.702192588540645, 0.297724511862993),
              627: (0.703708691019457, 0.296217118054471),
              628: (0.70516285342369, 0.294770292086239),
              629: (0.706563246693848, 0.293376153173208),
              630: (0.707917791621664, 0.29202710893484),
              631: (0.709230985413973, 0.290718622165321),
              632: (0.710500394495371, 0.289452941203169),
              633: (0.711724146175049, 0.288232104798955),
              634: (0.71290123112985, 0.28705732036371),
              635: (0.714031597116994, 0.28592887354565),
              636: (0.715117053483185, 0.284845106128776),
              637: (0.716159198599114, 0.283804449181674),
              638: (0.717158613642121, 0.282806411930931),
              639: (0.718116142602162, 0.281850256562656),
              640: (0.719032941629744, 0.280934951518654),
              641: (0.719911552942295, 0.280058078206728),
              642: (0.720752706639807, 0.279218959823395),
              643: (0.721554522486917, 0.27841951468527),
              644: (0.722314915560207, 0.277661870367724),
              645: (0.723031602573095, 0.276948357748342),
              646: (0.723701916040434, 0.276281836244226),
              647: (0.724328018926374, 0.275660074920571),
              648: (0.72491440513421, 0.275078184054899),
              649: (0.725466776098186, 0.274529977978249),
              650: (0.725992317541613, 0.274007682458387),
              651: (0.726494726713582, 0.273505273286418),
              652: (0.726974970468941, 0.273025029531059),
              653: (0.727431838038032, 0.272568161961968),
              654: (0.727864310792652, 0.272135689207348),
              655: (0.728271728271728, 0.271728271728272),
              656: (0.728656487100348, 0.271343512899652),
              657: (0.729020030309354, 0.270979969690646),
              658: (0.729360950694672, 0.270639049305328),
              659: (0.729677783237757, 0.270322216762243),
              660: (0.729969012837539, 0.270030987162461),
              661: (0.730233949140853, 0.269766050859146),
              662: (0.730474165302262, 0.269525834697738),
              663: (0.730693306723888, 0.269306693276112),
              664: (0.730896252242901, 0.269103747757099),
              665: (0.73108939558451, 0.26891060441549),
              666: (0.731279635919078, 0.268720364080922),
              667: (0.731467050901285, 0.268532949098715),
              668: (0.731649970922014, 0.268350029077986),
              669: (0.731826333484643, 0.268173666515357),
              670: (0.731993299832496, 0.268006700167504),
              671: (0.732150422161567, 0.267849577838433),
              672: (0.732299831084624, 0.267700168915376),
              673: (0.732442822871014, 0.267557177128986),
              674: (0.732581493590162, 0.267418506409838),
              675: (0.732718894009217, 0.267281105990783),
              676: (0.732858647268478, 0.267141352731522),
              677: (0.733000205253019, 0.266999794746981),
              678: (0.733141671137124, 0.266858328862876),
              679: (0.733281178934726, 0.266718821065274),
              680: (0.733416967225968, 0.266583032774032),
              681: (0.733550585847972, 0.266449414152028),
              682: (0.733683296435596, 0.266316703564404),
              683: (0.733812716688138, 0.266187283311862),
              684: (0.733935690314492, 0.266064309685508),
              685: (0.734047300312361, 0.265952699687639),
              686: (0.734142556896655, 0.265857443103345),
              687: (0.734221470250776, 0.265778529749224),
              688: (0.73428644636676, 0.26571355363324),
              689: (0.734340919958724, 0.265659080041276),
              690: (0.734390164995147, 0.265609835004853),
              691: (0.734437712655789, 0.265562287344211),
              692: (0.7344821704111, 0.2655178295889),
              693: (0.73452293055209, 0.26547706944791),
              694: (0.734559518422289, 0.265440481577711),
              695: (0.734591661642629, 0.265408338357371),
              696: (0.734621094712899, 0.265378905287101),
              697: (0.734648896835819, 0.265351103164181),
              698: (0.734673378010567, 0.265326621989433),
              699: (0.734690045444152, 0.265309954555848),
              700: (0.734690023258281, 0.265309976741719),
              701: (0.734689987139029, 0.265310012860971),
              702: (0.734690006501357, 0.265309993498643),
              703: (0.734690006621243, 0.265309993378757),
              704: (0.73468999733936, 0.26531000266064),
              705: (0.734690010322542, 0.265309989677458),
              706: (0.734690001779948, 0.265309998220052),
              707: (0.734689989928096, 0.265310010071905),
              708: (0.734689997524543, 0.265310002475457),
              709: (0.734690015028432, 0.265309984971568),
              710: (0.734689988232974, 0.265310011767026),
              711: (0.734690013992153, 0.265309986007847),
              712: (0.734690016799078, 0.265309983200922),
              713: (0.73468998731057, 0.26531001268943),
              714: (0.734689992515467, 0.265310007484533),
              715: (0.734690013707087, 0.265309986292913),
              716: (0.734690017589652, 0.265309982410348),
              717: (0.734690003073752, 0.265309996926248),
              718: (0.734689983373119, 0.265310016626881),
              719: (0.734689976107201, 0.265310023892799),
              720: (0.734690004148161, 0.265309995851839),
              721: (0.734689987681399, 0.265310012318601),
              722: (0.734689974353903, 0.265310025646097),
              723: (0.734689984824148, 0.265310015175852),
              724: (0.734689956808599, 0.265310043191401),
              725: (0.73468999960562, 0.26531000039438),
              726: (0.734689976446753, 0.265310023553247),
              727: (0.734689955409799, 0.265310044590201),
              728: (0.734690030031784, 0.265309969968216),
              729: (0.734689978026177, 0.265310021973822),
              730: (0.734689952045209, 0.265310047954791),
              731: (0.734690033024927, 0.265309966975073),
              732: (0.73468995791969, 0.26531004208031),
              733: (0.734689940400156, 0.265310059599844),
              734: (0.734690083270746, 0.265309916729254),
              735: (0.734689992493292, 0.265310007506708),
              736: (0.734689993262503, 0.265310006737497),
              737: (0.734690004102656, 0.265309995897344),
              738: (0.734689988466083, 0.265310011533917),
              739: (0.734689997004496, 0.265310002995504),
              740: (0.734690005712895, 0.265309994287105),
              741: (0.734690001061002, 0.265309998938998),
              742: (0.734689986019313, 0.265310013980687),
              743: (0.734690003235027, 0.265309996764973),
              744: (0.734689985970854, 0.265310014029147),
              745: (0.73469000015897, 0.26530999984103),
              746: (0.734689987259057, 0.265310012740943),
              747: (0.734690004447292, 0.265309995552708),
              748: (0.734689986053641, 0.265310013946359),
              749: (0.734690022445542, 0.265309977554458),
              750: (0.734690010703047, 0.265309989296953),
              751: (0.734689995519642, 0.265310004480358),
              752: (0.734690031649795, 0.265309968350205),
              753: (0.734690017035775, 0.265309982964225),
              754: (0.73469002018521, 0.26530997981479),
              755: (0.734690001849036, 0.265309998150965),
              756: (0.734689969923672, 0.265310030076328),
              757: (0.734690021473951, 0.265309978526049),
              758: (0.734689988508468, 0.265310011491531),
              759: (0.734690010940798, 0.265309989059202),
              760: (0.734689952045209, 0.265310047954791),
              761: (0.734689958511502, 0.265310041488498),
              762: (0.734690051943764, 0.265309948056236),
              763: (0.734689987703414, 0.265310012296586),
              764: (0.734689955549775, 0.265310044450225),
              765: (0.734689918842647, 0.265310081157353),
              766: (0.734690053566253, 0.265309946433747),
              767: (0.734690090428592, 0.265309909571407),
              768: (0.734690006317623, 0.265309993682377),
              769: (0.734689993716373, 0.265310006283627),
              770: (0.734689998971482, 0.265310001028518),
              771: (0.734690003046332, 0.265309996953668),
              772: (0.73469001265918, 0.265309987340821),
              773: (0.734689987869484, 0.265310012130516),
              774: (0.734690008119968, 0.265309991880032),
              775: (0.734689985247762, 0.265310014752238),
              776: (0.734690001171045, 0.265309998828956),
              777: (0.734689986762428, 0.265310013237572),
              778: (0.734690009355341, 0.265309990644659),
              779: (0.734689991422002, 0.265310008577998),
              780: (0.734689983741576, 0.265310016258424),
              781: (0.734690022025579, 0.265309977974421),
              782: (0.734689973773, 0.265310026227),
              783: (0.734690000588213, 0.265309999411786),
              784: (0.734690003434716, 0.265309996565284),
              785: (0.734689985247762, 0.265310014752238),
              786: (0.73468999874321, 0.26531000125679),
              787: (0.734689968813787, 0.265310031186213),
              788: (0.73469000085901, 0.26530999914099),
              789: (0.734690032239148, 0.265309967760853),
              790: (0.734689953954455, 0.265310046045545),
              791: (0.734689962693029, 0.265310037306971),
              792: (0.734690021977645, 0.265309978022356),
              793: (0.734689997973122, 0.265310002026878),
              794: (0.734690021714466, 0.265309978285534),
              795: (0.734689974603344, 0.265310025396656),
              796: (0.734690071104975, 0.265309928895025),
              797: (0.734690038597127, 0.265309961402873),
              798: (0.734690072330406, 0.265309927669594),
              799: (0.734689945925162, 0.265310054074838),
              800: (0.734689988020245, 0.265310011979755),
              801: (0.734690003519111, 0.265309996480889),
              802: (0.734690008017908, 0.265309991982092),
              803: (0.734690004773334, 0.265309995226666),
              804: (0.734689992552339, 0.265310007447661),
              805: (0.734689990778549, 0.265310009221451),
              806: (0.734689991319004, 0.265310008680996),
              807: (0.734690014718562, 0.265309985281438),
              808: (0.734689992876979, 0.265310007123021),
              809: (0.734689991099063, 0.265310008900937),
              810: (0.734689997844699, 0.265310002155301),
              811: (0.734690013288509, 0.265309986711491),
              812: (0.734690010610884, 0.265309989389116),
              813: (0.734690017049771, 0.265309982950229),
              814: (0.734689990304129, 0.265310009695871),
              815: (0.734690009460412, 0.265309990539588),
              816: (0.734689975482662, 0.265310024517338),
              817: (0.734689971329393, 0.265310028670607),
              818: (0.734689997544385, 0.265310002455615),
              819: (0.734689981787834, 0.265310018212166),
              820: (0.734689984286965, 0.265310015713035),
              821: (0.734690064939548, 0.265309935060452),
              822: (0.734690040936472, 0.265309959063528),
              823: (0.734690106944952, 0.265309893055048),
              824: (0.734689951098991, 0.265310048901009),
              825: (0.734689969847467, 0.265310030152533),
              826: (0.734689848977845, 0.265310151022155),
              827: (0.734689857284722, 0.265310142715278),
              828: (0.734690044343544, 0.265309955656456),
              829: (0.734690179345217, 0.265309820654783),
              830: (0.734689958783312, 0.265310041216688)}
