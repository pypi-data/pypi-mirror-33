.. This file is part of Sympathy for Data.
..
..  Copyright (c) 2010-2012 System Engineering Software Society
..
..     Sympathy for Data is free software: you can redistribute it and/or modify
..     it under the terms of the GNU General Public License as published by
..     the Free Software Foundation, either version 3 of the License, or
..     (at your option) any later version.
..
..     Sympathy for Data is distributed in the hope that it will be useful,
..     but WITHOUT ANY WARRANTY; without even the implied warranty of
..     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
..     GNU General Public License for more details.
..     You should have received a copy of the GNU General Public License
..     along with Sympathy for Data. If not, see <http://www.gnu.org/licenses/>.

Machine Learning Concepts
=============================

Machine learning is a method of data analysis that builds analytical
*models* based on empirical data. This models can be used for gaining
insight into the data, performing predictions or simply for transforming
the data. `Scikit-learn <http://scikit-learn.org/>`_ is a large
Open Source framework of machine learning algorithms that are included
in Sympathy for Data together with nodes and functions for accessing
scikit learn or adding upon available algorithms.

When working with machine learning in Sympathy a core datatype is the
*model* object. These objects represent both the algorithms and the
internal data created by the algorithms which are used for machine
learning. The source nodes of these types of models typically do not
directly perform any calculation on the data, which is rather done when
the models are applied to some dataset.

For example, if you start with a "Decision Tree Classifier" node and
run it, then you get an unfitted model object. By connecting the model
to a :ref:`Fit` node (uppermost port), and giving some example X
(middle port) and Y (bottom port) data, then you can "train" the model
from X. In the screenshot below the "Example dataset" node has been
configured to use the "Iris" dataset. On the right side we can see the
output model created by the Fit node. This displays the learned decision
tree. This visualization requires that Graphviz/dot is installed and
configured.

.. figure:: screenshot_machinelearning_basic.png
   :scale: 50%
   :alt: A small machine learning example.
   :align: center

After fitting (a.k.a. training) a model you can use it to, for example, do
predictions on data. This data must have the same columns as the
original X data, and will produce a table with the same columns as the
original Y data.

Pre-processing data
-------------------

In addition to models that can perform predictions of data it is also
possible to use models that do other operations such as preprocessing
the input data. Examples of such nodes include the "Standard scaler"
which removes the mean of the data and rescales the data to have a
unit standard deviation. In order to use models of this type you
typically want to use the "Fit transform" to let the model "learn"
what the rescaling parameters should be and to output the transformed
data.

If you later want to perform the *same* transformation on another
dataset you can use the "transform" node with model coming as an
output from the earlier fit and transform. For example, in the flow
below the mean of each column in A will be subtracted from the
corresponding columns in B. Note that the *order* of the columns
and not only their names matter when applying a node.

.. figure:: screenshot_fittransform.png
   :scale: 75%
   :alt: Example of using preprocessing nodes.
   :align: center

Note that you could have used a :ref:`Fit` node instead of :ref:`Fit
Transform` here for the same result since the rescaled version of A is
not used here.

In a real application the model given by fitting or training A would
typically be exported to disk using the "Export model" node, and
imported back in another flow when using it for transforming or
predicting on the B dataset.

Varying number of parameters
----------------------------

Depending on the types of models that are used the :ref:`Fit` node can take
either one (X) or two (X, Y) tables with inputs. Since the X-Y case is
the most common, this is the default, and if you want to pass only one
input (eg. when fitting a preprocessing node) you can right click on
the Y port and select "delete port".

Other nodes that can take a varying number of parameters are the
*pipeline* and *voting classifier* nodes. In order to add *more*
inputs to these you can right click on the node and select "Create
input port -> models". This way of adding/removing input ports works
also on some other nodes in Sympathy, test for instance the tuple or
zip nodes.

Pipelines
---------

In a typical machine learning application one often needs to perform
multiple pre-processing steps on the data before it is given to a
machine learning algorithm for training or prediction. To simplify
multiple pre-processing steps a complex *pipeline* model can be
created out of simpler models.

These pipeline models give the data to each constituent model one at
a time and transforms it before passing to the next model. When
performing a training or prediction task, the last model performs
the actual training or predictions.

.. figure:: screenshot_pipeline.png
   :scale: 50%
   :alt: Pipeline example expanding inputs with polynomial features
         before a logistic regression
   :align: center

In the example above a "Polynomial features" node is used to create
all polynomials of degree two from the features in the Iris dataset. These
new features include, for example, petal width * petal height, petal width^2,
etc.  By pipelining this polynomial feature node to the logistic
regression node we can improve the final output score from circa 95% to 100%.

Note that in the example above we do not use the same data to train
the model and to score it. The node "Simple train-test split" splits
the X and Y data into 75% that are used for training (top two output
ports) and 25% that are used for evaluating how well the model learned
the data (bottom two output ports).

This is only one example of how datasets can be used when evaluating
models, for more advanced methods use the cross-validation nodes. You
should also avoid leaking information from the test set into your
choice of parameters by further splitting the data which is used during
development and during final evaluation.

Machine learning examples
-------------------------

Many more algorithms and concepts from machine learning have been
integrated with Sympathy, for more examples make sure to open the
examples that are included with the Sympathy release. You can find the
examples folder under the install path of Sympathy.

Examples of concepts that are covered by these examples:

- Integration with the image processing parts of Sympathy
- Face recognition of politicians using the eigenfaces method
- Training multiple times using different "hyper parameters" to find
  the configurations that are best for a given problem
- Using cross-validation when learning hyper-parameters
- Combining ensembles of simple classifiers for more robust classifications
- Operating on text data using the bag-of-words method
- Analyzing the quality of the trained model using ROC
  (receiver-operating characteristic) curves, confusion matrices, and
  other metrics
- Using clustering algorithms as preprocessing steps for supervised
  learning algorithms


..
   Deep learning on GPUs
   ---------------------

   You can use the Tensor nodes in Sympathy to implement deep learning if
   you have GPU hardware and the required drivers and toolkits
   installed. This form of machine learning is implemented on top of the
   `Keras <https://keras.io/>`_ library for deep learning. Although not
   all functionalities of Keras have yet been implemented many
   state-of-the-art algorithms can be implemented purely graphically
   through Sympathy.

   To get started you need to install either
   `Google Tensorflow <https://www.tensorflow.org/install/>`_ with GPU support
   OR `Theano <http://deeplearning.net/software/theano/>`.
   After installing, make sure that Python can find the libraries and that they
   can run using the GPU.

   The Keras library that comes with Sympathy for Data will default to attempt to
   use TensorFlow, but will attempt Theano if tensorflow fails to load.

   Keras Server
   ^^^^^^^^^^^^

   Due to limitations in how the underlying backends handle GPU support there can
   only be one process at a time that use the GPU. For this purpose Sympathy for
   Data launches a Keras-Server process the first time that any such calculations
   are attempted. It is also possible to use a Keras-server process that is
   running on the local network. To do so, start by launching Sympathy for Data
   on the server machine and run the node "Tensor: force server". Next, give the
   IP address or DNS name of the server computer as the environment variable
   "KERAS_SERVER" on the client machines. For example:

   .. code-block:: bash

      export KERAS_SERVER=10.123.123.123

   Where 10.123.123.123 is the IP address of the machine where you started the
   server. In case you need to setup port forwarding the server uses
   port 7257 (TCP/IP).

   Note that only one GPU request at a time can be handled by the server, it is
   not recommended to have multiple clients connected at the same time.

   Building deep learning networks
   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

   Once you have Keras and TensorFlow (or Theano) setup and working you can start
   developing deep learning models. The basic workflow is that you create a number
   of *Tensor blueprints* that represent the internal structure of your model,
   such as the type of layers, their parameters and topology.

   For an example see the tensors below that describe a machine learning
   network that takes 28x28 images as inputs, uses two layers of
   convolution matrices and gives the combined output from the first and
   the second layer as input to a fully connected (dense) layer. By using dropout
   and L2 regularization it achieves approximately 99.4% accuracy on the famous
   MNIST dataset for recognising handwritten digits.

   .. figure:: screenshot_mnist_tensors.png
      :scale: 50%
      :alt: Example of tensor blueprints creating a deep learning network
      :align: center

   Each individual tensor blueprint node can be configured to setup parameters
   such as number of nodes, type of activation functions and regularization
   for the different layers. For this purpose each tensor blueprint should atleast
   be configured to give it a unique *name* which is used when accessing these
   parameters from a finished model.

   These blueprints are
   then given to the *Tensor: as model* node, which creates a machinelearning
   model from them. This model use the same interfaces as all the other machine
   learning models in Sympathy for Data and can be given to the normal nodes for
   fitting, predicting, scoring etc.

   This nodes takes two inputs, the first should be
   tensor that should be given the inputs, and the second the tensor that contain
   the outputs. You can add additional input/output ports by right-clicking on the
   node and selecting 'Create input port'.

   If you open the view for this model you will see a table of all
   parameters as well as a summary of the topology of the network. This view is
   useful to check if you are unsure how many units have been created in each
   layer.

   .. figure:: screenshot_mnist_vis.png
      :scale: 50%
      :alt: Visualization of the
      :align: center

   When fitting a model with multiple
   inputs or outputs then the X and Y training data are split in the same order as
   the inputs are given.

   For example, lets assume that you have constructed a network with an
   input A of size 2, and input B of size 3 and have given A and B to the
   model construction in that order. This model then expects the total
   size of X to be 5, and the first 2 columns will be given to A and the
   remaining 3 given to B. It is an error to have more columns in X than
   the sum of the input sizes.

   For the full example that performs deep learning on the MNIST dataset see the
   machine learning example mnist_deeplearning.
