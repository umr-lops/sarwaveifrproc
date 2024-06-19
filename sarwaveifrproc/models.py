from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Concatenate, Input, Dropout

def get_model(version):
    """
    Retrieves a neural network model builder function based on the specified version.

    Parameters:
    - version (str): A string indicating the version of the model to retrieve.

    Returns:
    - model_builder (function): A function that builds the specified version of the neural network model.
    """
    model_builders = {'1.0.0': build_model_v1_0_0,
                      '1.0.1': build_model_v1_0_0}

    return model_builders[version]


def build_model_v1_0_0(nb_classes):
    """
    Builds a neural network model corresponding to the version v1.0.0.

    Parameters:
    - nb_classes (list or tuple): A list or tuple containing the number of output classes for each output layer.

    Returns:
    - model (keras.Model): A compiled Keras model with the specified architecture.

    Architecture:
    - Input layer: 24 features.
    - 10 Dense layers, each with 1024 neurons and ReLU activation.
    - Output layer: Concatenation of output layers with a number of neurons specified by nb_classes.

    """
    input_shape = (24, )
    X_input = Input(input_shape)
    
    X = Dense(1024, activation='relu')(X_input)
    for i in range(9):
        X = Dense(1024, activation='relu')(X)
        
    X_output = Concatenate()([Dense(n)(X) for n in nb_classes])
    
    model = Model(inputs=X_input, outputs=X_output)
    model.compile()

    return model