# DICOM Contrast Enhancement Tool 🔍

![GUI Screenshot](./images/gui-screenshot.png)

A user-friendly GUI application for enhancing contrast in CT DICOM images using a linear transformation equation. This tool helps medical professionals and researchers improve the visibility of CT scan details while preserving crucial DICOM metadata.

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Features

- **Intuitive GUI Interface**: Easy-to-use graphical interface for batch processing DICOM files
- **Customizable Enhancement**: Adjust contrast using the equation `y = ax - b` where:
  - `a`: Coefficient for contrast adjustment (default: 1.22)
  - `b`: Constant offset value (default: 5)
- **Batch Processing**: Process multiple DICOM files simultaneously
- **Metadata Preservation**: Maintains all essential DICOM tags and metadata
- **Progress Tracking**: Real-time progress monitoring with detailed logs
- **Debug Information**: First-image processing details for verification
- **DICOM Compliance**: Preserves DICOM format and compatibility

## 🚀 Installation

1. Download the latest release from the [releases page](link-to-releases)
2. Extract the ZIP file to your desired location
3. Run the `DicomEnhancer.exe` executable

No additional installation or Python environment required!

## 📖 How to Use

1. **Launch the Application**
   - Double-click the `DicomEnhancer.exe` file

2. **Configure Enhancement Parameters**
   - Set the coefficient (a) - default is 1.22
   - Set the constant (b) - default is 5

3. **Select Folders**
   - Click "Browse" to select input folder containing DICOM files
   - Click "Browse" to select output folder for enhanced images

4. **Process Images**
   - Click "Process Images" to start enhancement
   - Monitor progress in the log window
   - Wait for completion message

## 📋 Requirements for Source Code

If you want to run from source:

- Python 3.7+
- Required packages:
  - pydicom
  - numpy
  - tkinter (usually comes with Python)

## 🔬 Technical Details

### Enhancement Algorithm

The contrast enhancement is performed using the linear transformation:
```
Enhanced_Value = a * Original_Value - b
```

The tool automatically handles:
- Proper scaling of Hounsfield Units (HU)
- DICOM metadata preservation
- Bit depth maintenance
- Data type consistency

### DICOM Tags

The following DICOM tags are carefully preserved:
- Rows and Columns
- Bits Allocated/Stored
- High Bit
- Pixel Representation
- Samples Per Pixel
- Photometric Interpretation

Additional processing information is stored in custom tags:
- 0x00071001: Processing method
- 0x00071002: Enhancement equation

## ⚠️ Important Notes

- Always backup your original DICOM files before processing
- Verify enhancement results before clinical use
- The tool preserves original DICOM metadata but adds processing information
- Not intended for primary diagnostic use

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

If you encounter any issues or have questions:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information about your problem
3. Include sample files if possible (without patient data)

## 🙌 Acknowledgments

- PyDICOM community for the excellent DICOM handling library
- Medical imaging professionals for valuable feedback