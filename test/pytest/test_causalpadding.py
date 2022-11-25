import pytest
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D
import numpy as np
import hls4ml
from pathlib import Path

test_root_path = Path(__file__).parent

atol = 5e-3

@pytest.mark.parametrize('io_type', ['io_stream', 'io_parallel'])
@pytest.mark.parametrize('backend', ['Vivado', 'Quartus'])
def test_validpadding(io_type, backend):
    
    model = Sequential()
    model.add(Conv1D(1, 5, padding="causal"))
    model.compile()

    data = np.random.normal(0, 1, 100)

    config = hls4ml.utils.config_from_keras_model(model,
                                                  default_precision='ap_fixed<32,1>',
                                                  granularity='name')
    odir = str(test_root_path / f'hls4mlprj_validpadding_{backend}_{io_type}')
    hls_model = hls4ml.converters.convert_from_keras_model(model,
                                                           hls_config=config,
                                                           io_type=io_type,
                                                           output_dir=odir,
                                                           backend=backend)
    hls_model.compile()

    # Predict
    y_keras = model.predict(data).flatten()
    y_hls = hls_model.predict(data).flatten()
    np.testing.assert_allclose(y_keras, y_hls, rtol=0, atol=atol, verbose=True)
