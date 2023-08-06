# Machine learning tools for remote sensing data

---

## 1. Installation

Depends on Python 3, numpy, pandas, scikit-learn, GDAL, lxml

### PYTHON Environment

Try the installation of Anaconda/Miniconda package [link: <https://conda.io/miniconda.html>]. Use the Python 3.6 version.

### Installing Prerequisites

Recommend to use the `conda-forge` repository. After the installation of Miniconda (or Anaconda), run the following commands in command line tool one by one.

~~~~~~
conda config --add channels conda-forge
conda install scikit-learn
conda install pandas
conda install pytables
conda install lxml
conda install gdal
~~~~~~

### Install package: learn2map

~~~~~~
pip install learn2map
~~~~~~


---

## 2. Command-Line Tools

### rf_estimator -- Random Forest Estimator

#### Usage:

~~~~~~
rf_estimator -i "input" -o "outname" [-n "n_trees_step" -s "min_smpl_step" -f "max_ftr_step"]
~~~~~~

* `"input"` - location of input filename (e.g. `'./input_file_list.txt'`). It should be a txt file includes the individual input filename at each line (all files should be in `geotiff` format registered to have the same dimension and spatial resolution):

    - 1st line specifies the filename of the mask file (could be a file denoting 0 as invalid, and 1 as valid pixels).

    - 2nd line specifies the filename of the interested variable (e.g. the file containing AGB measurements for some pixels).

    - All the rest lines can be filenames of environmental layers used as input data for spatial mapping.

* `"outname"` - location of output filename with no file extension, as multiple files will be generated using it as basename (e.g. `'./output/drc_agb'`).

* `n`, `s`, `f` - parameters used in algorithm optimization. It accepts integer values. Small numbers will increase the running time of the algorithm.

* **Final output**: geotiff file named as `"outname"_env_est_raster.tif`. It contains the prediction map of your interested variable -- the 2nd layer specified in `"input"`.

#### Explanation of intermediate outputs:

* `"outname".vrt` -- [virtual format](http://www.gdal.org/drv_vrt.html) file for the stack of all input files

* `"outname"_training.h5` -- hdf5 file to save the table storing information on valid training pixels

* `"outname"_env.h5` -- hdf5 file to save the table storing information on valid land pixels (defined by the 1st line, the mask file, in `"input"` )

* `"outname"_env_est.h5` -- hdf5 file to save the table storing Random Forest predictions for all valid land pixels (should have the same rows as `"outname"_env.h5`)

* `"outname"_env_est.csv` -- csv file converted from `"outname"_env_est.h5`

* `"outname"_env_est_raster.vrt` -- virtual format file wrapping `"outname"_env_est.csv` so as to become a valid OGR file

* `"outname"_env_est_raster.tif` -- Final Output. Geotiff file that contains the prediction map of your interested variable -- the 2nd layer specified in `"input"`.

---

### csv_output -- Output CSV file

#### Usage:

~~~~~~
csv_output -i "input" -o "outname"
~~~~~~

* `"input"` - location of input filename (e.g. `'./input_training.txt'`). It should be a txt file includes the individual input filename at each line (all files should be in `geotiff` format registered to have the same dimension and spatial resolution):

    - 1st line specifies the filename of the interested variable for training/test (e.g. valid pixels with AGB>0).

    - 2nd line specifies the filename of the prediction map (e.g. the output file `"outname"_env_est_raster.tif` from the command `rf_estimator`).

    - The rest lines can be filenames of environmental layers that should output along with the 1st and 2nd layers.

* `"outname"` - location of output filename with no file extension, as multiple files will be generated using it as basename (e.g. `'./output/drc_training'`).

---

## 3. Python Modules

### raster_tools.py

Out-of-core tools for raster data analysis.

#### Functions:

1. raster_clip - For every input raster file, get the same spatial resolution,
projection, and extent as the reference raster.

2. build_stack_vrt - Build stacked virtual raster for all registered rasters.

3. raster_to_h5 - Out-of-core reformat of rasters to pandas dataframe using the
virtual raster as input. Dataframe is stored in hdf5 format.

4. ogrvrt_to_grid - Convert scattered points to raster. Point data set is stored
in csv format, and output is in geotiff format.

5. h5_to_csv - Reformat h5 to csv file in chunks.

---

### data_learning.py

Machine learning model setup.

#### Class:

GridLearn - Build the machine learning object.

* Properties
  - in_file: input h5 file that contains the training data
  - y_column: column name for response variable y
  - mask_column: column name for mask
  - best_params: param set that can be used in further learning
  - mdl: defined model pipeline

* Methods
  - setup_rf_model: Set up the random forest model.
  - tune_param_set: Find the best parameter set that is used in learning.
  - predict_bigdata: sklearn and prediction for data chunks
