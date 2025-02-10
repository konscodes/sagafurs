import unittest

from main import extract_data_from_pdf


class TestExtractDataFromPDF(unittest.TestCase):

    def test_extract_data_from_pdf(self):
        # Sample PDF path (you need to replace this with an actual test PDF path)
        pdf_path = './import/sblueM JUN23.pdf'

        # Expected data structure
        expected_data = [{
            'size': 'M',
            'color': 'Blue',
            'price_sroy': '10.5',
            'price_saga': '12.3'
        }, {
            'size': 'L',
            'color': 'Red',
            'price_sroy': '11.0',
            'price_saga': '13.0'
        }]

        # Extract data from PDF
        data = extract_data_from_pdf(pdf_path)

        # Check if the extracted data matches the expected data
        self.assertEqual(data, expected_data)


if __name__ == '__main__':
    unittest.main()
