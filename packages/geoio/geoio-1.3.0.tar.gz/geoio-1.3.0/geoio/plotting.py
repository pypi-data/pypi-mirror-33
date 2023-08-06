import tinytools as tt
import numpy as np
import matplotlib.pyplot as plt
import logging
import plotly.graph_objs as go
import plotly.colors as plc

import geoio

logger = logging.getLogger(__name__)

# Currently doesn't return figure handles to help with memory size issues on
# large images.  This could probably use a close look at ways to make it
# more efficient:
# https://pypi.python.org/pypi/ModestImage
# https://github.com/ipython/ipython/issues/1623/
# http://stackoverflow.com/questions/15345336/memory-leak-in-matplotlib-imshow

def imshow(data, ax=None, stretch=[0.02,0.98], stretch_type='linear',
           mask_values=0.0):
    """Convenience method to do all the plotting gymnastics to get a reasonable
    looking image plot.

    Input:
    data            numpy array in gdal band order - 3 dimensions (bands, x, y)
    stretch         stretch values on a scale of [0,1]
    stretch_type    type of stretch scale (only linear is currently supported)
    """

    if len(data.shape) == 2:
        data = np.repeat(data[np.newaxis,:,:],3,axis=0)

    if data.shape[0] == 1:
        data = np.repeat(data,3,axis=0)

    if len(data.shape) != 3:
        raise ValueError('This convenience function is only implemented ' \
                         'for three bands.  Use img.get_data(bands=...) to ' \
                         'retrieve specific data.')
                        # ToDo - This could also be speed up by indexing a
                        # single numpy array.

    # define stretch
    # Possibly useful code for additional stretches at:
    # http://scikit-image.org/docs/dev/api/skimage.exposure.html
    # also
    # http://scikit-image.org/docs/dev/auto_examples/plot_equalize.html
    if stretch_type == "linear":
        pass
    else:
        raise ValueError('The passed value of stretch is not implemented.')

    # Get the per-band scaled data
    data = tt.np_img.conv_to_bandslast(data)
    data = data.astype('float32')

    # Mask out (presumably) nodata value(s)
    if mask_values is None:
        dmasked = data.reshape(-1,3)
    else:
        # collapse to a 2D boolean where elements are False when all bands
        # contain a value in mask_values.
        if not isinstance(mask_values, list):
            mask_values = [mask_values]
        m = ~np.all(np.in1d(data,mask_values).reshape(data.shape),axis=2)
        dmasked = data[m,:]

    # Handle binary and singleton arrays, otherwise use stretch val.
    ulen = len(np.unique(dmasked))
    if ulen == 2:
        lims = np.percentile(dmasked,(0,100),axis=0)
        logger.warn('This looks like a binary image so falling back to a '
                    '0-100% stretch.')
    elif ulen == 1:
        lims = np.array([np.array([0.0,0.0,0.0]),np.array([1.0,1.0,1.0])])
        logger.warn('This looks like a singleton image so falling back to a '
                    '0-1 stretch to try and correctly plot the presumably '
                    'boolean value.')
    elif ulen == 0:
        lims = np.array([np.array([0.0, 0.0, 0.0]), np.array([1.0, 1.0, 1.0])])
        logger.warn('No unmasked data found, defaulting to a 0-1 stretch.')
    else:
        lims = np.percentile(dmasked,[x*100 for x in stretch],axis=0)

    for x in range(len(data[0,0,:])):
        top = lims[:,x][1]
        bottom = lims[:,x][0]
        if top-bottom == 0:
            top = 1.0
            bottom = 0.0
            logger.warn('The requested stretch resulted in no change in the '
                        'data space.  Defaulting to the original data.')
        data[:,:,x] = (data[:,:,x]-bottom)/float(top-bottom)
    data = np.clip(data,0,1)

    # Get plot axes
    if ax is None:
        ax = plt.gca()

    # Definitely not the most memory efficient for a single band image.
    if data.shape[2] in [3,4]:
        iii = ax.imshow(data, interpolation='nearest')
    elif data.shape[2] == 1:
        iii = ax.imshow(data[:,:,0], interpolation='nearest')
    else:
        raise ValueError("No plotting done, bad dimensions")

    # ToDo: fix memory issues - see comments above
    # Return the AxesImage handle so that you can pass it to things like
    # plt.colorbar(AxesImage_obj, ax=ax_handle)
    return iii

# @profile
def imshow_new(data, ax=None, stretch=[0.02,0.98], stretch_type='linear',
               no_data_value=0.0, approx=True):
    """Convenience method to do all the plotting gymnastics to get a reasonable
    looking image plot.

    Input:
    data            numpy array in gdal band order - 3 dimensions (bands, x, y)
    stretch         stretch values on a scale of [0,1]
    stretch_type    type of stretch scale (only linear is currently supported)
    """

    if len(data.shape) == 2:
        data = np.repeat(data[np.newaxis,:,:],3,axis=0)

    if data.shape[0] == 1:
        data = np.repeat(data,3,axis=0)

    if len(data.shape) != 3:
        raise ValueError('This convenience function is only implemented ' \
                         'for three bands.  Use img.get_data(bands=...) to ' \
                         'retrieve specific data.')
                        # ToDo - This could also be speed up by indexing a
                        # single numpy array.

    # define stretch
    # Possibly useful code for additional stretches at:
    # http://scikit-image.org/docs/dev/api/skimage.exposure.html
    # also
    # http://scikit-image.org/docs/dev/auto_examples/plot_equalize.html
    if stretch_type == "linear":
        pass
    else:
        raise ValueError('The passed value of stretch is not implemented.')

    # helper functions adapted from :
    # http://stackoverflow.com/questions/14464449/using-numpy-to-efficiently-convert-16-bit-image-data-to-8-bit-for-display-with
    def display(image, display_min, display_max):  # copied from Bi Rico
        # Here I set copy=True in order to ensure the original image is not
        # modified. If you don't mind modifying the original image, you can
        # set copy=False or skip this step.
        image = np.array(image, copy=True)
        image.clip(display_min, display_max, out=image)
        image -= display_min
        image //= int(round((display_max - display_min + 1) / 256.0))
        return image.astype(np.uint8)

    def lut_display(image, display_min, display_max):
        lut = np.arange(2 ** 16, dtype='uint16')
        lut = display(lut, display_min, display_max)
        return np.take(lut, image)

    # Move bands to the end for matplotlib
    data = tt.np_img.conv_to_bandslast(data)

    ### Get the per-band scaled data
    ## Prep for the scaling calculation
    # Set no data value for pixel extraction
    if no_data_value is None:
        ndv = None
    else:
        ndv = no_data_value

    # Set nsamp from approx argument
    if isinstance(approx, bool):
        if approx:
            nsamp = np.prod(data.shape[1:]) * 0.10
        else:
            nsamp = None
    elif isinstance(approx, float):
        if (approx > 1.0) or (approx < 0.0):
            raise ValueError('If approx is a float, it should be between '
                             '0.0 and 1.0')
        else:
            nsamp = np.prod(data.shape[1:]) * approx
    else:
        raise ValueError('Value of approx is not valid')



    ## Pull limits from the data
    lims = []
    for band in range(data.shape[-1]):
        band_flat = data[:,:,band].ravel()
        band_flat = band_flat.take(np.where(band_flat!=ndv)[0])
        tb = np.percentile(band_flat, [int(x * 100) for x in stretch])
        lims.append(tb)
        del band_flat

    ## Make 8-bit arrays for matplotlib
    shp_8bit = list(data.shape)
    shp_8bit[2] = shp_8bit[2]+1
    data_8bit = np.empty(shp_8bit, np.uint8)
    for band in range(data.shape[-1]):
        bottom, top = list(lims[band].astype(np.uint16))
        data_8bit[:,:,band] = lut_display(data[:,:,band], bottom, top)
    data_8bit[:,:,3] *= 255

    #######
    # Maybe the best approach is to test for int
    # if uint 8 - pass on or scale as needed
    # if uin16 or int16 - run lut_to_uin8 and scale if needed
    # if float, scale to 0,1 and move on.

    # Get plot axes
    if ax is None:
        ax = plt.gca()

    # Definitely not the most memory efficient for a single band image.
    if data_8bit.shape[2] in [3,4]:
        iii = ax.imshow(data_8bit, interpolation='nearest')
    elif data.shape[2] == 1:
        iii = ax.imshow(data_8bit[:,:,0], interpolation='nearest')
    else:
        raise ValueError("No plotting done, bad dimensions")

    # ToDo: fix memory issues - see comments above
    # Return the AxesImage handle so that you can pass it to things like
    # plt.colorbar(AxesImage_obj, ax=ax_handle)
    return iii

def hist(data):
    """Convenience method to do all the plotting gymnastics to get a reasonable
    looking histogram plot.

    Input: data - numpy array in gdal format - (bands, x, y)

    Returns:  matplotlib figure handle

    Adapted from:
    http://nbviewer.jupyter.org/github/HyperionAnalytics/PyDataNYC2014/blob/master/color_image_processing.ipynb
    """

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plt.hold(True)
    for x in range(len(data[:,0,0])):
        counts, edges = np.histogram(data[x,:,:],bins=100)
        centers = [(edges[i]+edges[i+1])/2.0 for i,v in enumerate(edges[:-1])]
        ax1.plot(centers,counts)
    plt.hold(False)

    plt.show(block=False)

    return ax1


def my_scatter_continuous_error(x_values, y_values, y_errors=None,
                                ds_names=None,
                                title=None, xlabel=None, ylabel=None,
                                ds_colors=None):
    """Box plot function with reasonable defaults

    Inputs:
        x_values : List of x points for the scatter points, must be
                   the same size of the elements of y_values.
        y_values : List of y points for the scatter points.
        y_errors : List of y_errors for the scatter points.  If the
                   shape is (data_points, 2), the second dimensions
                   is taken to delineate a different +/- y_error.

    Returns:
        fig : plot.ly figure object

    """

    ### Test/Clean inputs
    assert len(x_values) == len(
        y_values), "Number of data sets in x_values and y_values is inconsistent"

    if y_errors is None:
        y_errors = [None for x in y_values]

    if ds_colors is None:
        # add code to cycle colors!!!
        ds_colors = plc.DEFAULT_PLOTLY_COLORS
    else:
        if not isinstance(ds_colors, list):
            raise ValueError("ds_colors must be a list")
        pass  # This will cycle and reuse the colors passed in.
        # assert len(ds_colors) >= len(x_values), "Wrong number of ds_colors passed in"

    if ds_names is None:
        ds_names = ['trace' + str(x) for x in range(len(x_values))]

    traces = []
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        trace = go.Scatter(x=x,
                           y=y,
                           mode='lines+markers',
                           name=ds_names[i],
                           line=go.Line(color=ds_colors[i % len(ds_colors)]))

        if y_errors[i]:
            trace_lower = go.Scatter(x=x,
                                     y=[yyy - sss for (yyy, sss) in
                                        zip(y, y_errors[i])],
                                     mode='lines',
                                     name=ds_names[i] + '-lower',
                                     line=go.Line(
                                         color=ds_colors[i % len(ds_colors)],
                                         width=0),
                                     fill='tonexty',
                                     showlegend=False)

            trace_upper = go.Scatter(x=x,
                                     y=[yyy + sss for (yyy, sss) in
                                        zip(y, y_errors[i])],
                                     mode='lines',
                                     name=ds_names[i] + '-upper',
                                     line=go.Line(
                                         color=ds_colors[i % len(ds_colors)],
                                         width=0),
                                     showlegend=False)

            traces.append(trace_upper)
            traces.append(trace_lower)
            traces.append(trace)
        else:
            traces.append(trace)

        layout = go.Layout(
            xaxis=dict(title=xlabel),
            yaxis=dict(title=ylabel),
            title=title)

    return go.Figure(data=traces, layout=layout)


def my_boxplot(ds, ds_xpoints=None, ds_names=None, outliers=True,
               title=None, xlabel=None, ylabel=None,
               ds_colors=None):
    """Box plot function with reasonable defaults

    Inputs:
        ds : List of data sets with each element of ds of shape [num_data_points, num_groups]

    Returns:
        fig : plot.ly figure object

    """

    ### Clean inputs
    # Clean inputs of the same length as the number of data sets in ds
    nds = len(ds)

    if ds_names is None:
        ds_names = [None for x in range(nds)]
    else:
        assert len(ds_names) == nds, "Wrong number of ds_names passed in"

    if ds_colors is None:
        pass
    else:
        assert len(ds_colors) >= nds, "Wrong number of ds_colors passed in"

    # Clean inputs of the same length as the number of groups in each ds element
    ngroups = ds[0].shape[-1]
    assert all([x.shape[-1] == ngroups for x in
                ds]), "All ds inputs should have the same number of groups"

    if ds_xpoints is None:
        ds_xpoints = ['Group' + str(x) for x in range(ngroups)]
    else:
        assert len(
            ds_xpoints) == ngroups, "Wrong number of ds_xpoint passed in"

    ### Set up data traces
    traces = []
    for i, (data, dsn) in enumerate(zip(ds, ds_names)):
        box = go.Box(
            y=data.flatten(),
            x=ds_xpoints * len(data),
            boxpoints=False,
            name=dsn)

        if ds_colors:
            box['marker'] = go.Marker(color=ds_colors[i])

        if outliers:
            box['boxpoints'] = 'outliers'

        traces.append(box)

    ### Set up Layout
    layout = go.Layout(
        yaxis=go.YAxis(title=ylabel, zeroline=False),
        xaxis=go.XAxis(title=xlabel),
        title=title,
        boxmode='group'
    )

    # Return figure for editing or plotting
    return go.Figure(data=traces, layout=layout)


if __name__ == '__main__':

    img = geoio.DLImage('meta_LC80200332016235_v1')
    d = img.get_data(bands='RGB')
    # d = img.get_data(bands='RGB', window=[6000, 6000, 3000, 3000])

    imshow_new(d)
    # imshow(d)