import pytest
from unittest.mock import patch, call, MagicMock

from point_utils.utils import visualize


@patch('builtins.print')
@patch('point_utils.utils.plt')
@patch('point_utils.utils.get_data_from_txt')
def test_visualize(mock_get_data_from_txt, mock_plt, mock_print):
    # Mock the return value of get_data_from_txt
    mock_get_data_from_txt.return_value = (
        [[1, 2, 3], [4, 5, 6]],  # coordinates
        ['label1', 'label2']  # labels
    )
    mock_plt.gca = MagicMock()
    mock_plt.gca().get_legend_handles_labels.return_value = (
        ['handle1', 'handle2'], ['label1', 'label2'])

    output_file = 'dummy_output.png'
    visualize('dummy_input.txt', output_file)
    # Check if the print statement was called with the correct argument
    assert call(f'Saved plot to {output_file}.') in mock_print.call_args_list

    # Ensure plt methods are called
    assert mock_plt.figure.called
    assert mock_plt.savefig.called
    assert mock_plt.show.called