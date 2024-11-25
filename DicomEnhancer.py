import pydicom
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

class DicomEnhancerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM Contrast Enhancement")
        
        # Set window size and position
        window_width = 700
        window_height = 500
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Initialize variables
        self.input_folder = ""
        self.output_folder = ""
        
        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Equation frame
        equation_frame = tk.LabelFrame(self.root, text="Contrast Enhancement Equation: y = ax - b", pady=10, padx=10)
        equation_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Coefficient 'a' input
        coef_a_frame = tk.Frame(equation_frame)
        coef_a_frame.pack(fill=tk.X, pady=5)
        tk.Label(coef_a_frame, text="Coefficient (a):").pack(side=tk.LEFT)
        self.coef_a_var = tk.StringVar(value="1.22")
        tk.Entry(coef_a_frame, textvariable=self.coef_a_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Coefficient 'b' input
        coef_b_frame = tk.Frame(equation_frame)
        coef_b_frame.pack(fill=tk.X, pady=5)
        tk.Label(coef_b_frame, text="Constant (b):  ").pack(side=tk.LEFT)
        self.coef_b_var = tk.StringVar(value="5")
        tk.Entry(coef_b_frame, textvariable=self.coef_b_var, width=10).pack(side=tk.LEFT, padx=5)

        # Input folder selection
        input_frame = tk.LabelFrame(self.root, text="Folder Selection", pady=10, padx=10)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        input_folder_frame = tk.Frame(input_frame)
        input_folder_frame.pack(fill=tk.X, pady=5)
        tk.Label(input_folder_frame, text="Input Folder:").pack(side=tk.LEFT)
        self.input_path_var = tk.StringVar()
        tk.Entry(input_folder_frame, textvariable=self.input_path_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(input_folder_frame, text="Browse", command=self.select_input_folder).pack(side=tk.LEFT)

        # Output folder selection
        output_folder_frame = tk.Frame(input_frame)
        output_folder_frame.pack(fill=tk.X, pady=5)
        tk.Label(output_folder_frame, text="Output Folder:").pack(side=tk.LEFT)
        self.output_path_var = tk.StringVar()
        tk.Entry(output_folder_frame, textvariable=self.output_path_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(output_folder_frame, text="Browse", command=self.select_output_folder).pack(side=tk.LEFT)

        # Process button
        process_button = tk.Button(self.root, text="Process Images", 
                                 command=self.process_images,
                                 bg="#4CAF50", fg="white")
        process_button.pack(pady=10)
        process_button.config(pady=10, padx=20)

        # Progress text
        progress_frame = tk.LabelFrame(self.root, text="Progress Log", pady=5, padx=5)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.progress_text = tk.Text(progress_frame, height=10, width=60)
        self.progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def select_input_folder(self):
        self.input_folder = filedialog.askdirectory(title="Select Input Folder")
        self.input_path_var.set(self.input_folder)

    def select_output_folder(self):
        self.output_folder = filedialog.askdirectory(title="Select Output Folder")
        self.output_path_var.set(self.output_folder)

    def validate_coefficients(self):
        try:
            a = float(self.coef_a_var.get())
            b = float(self.coef_b_var.get())
            return True, a, b
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for coefficients")
            return False, None, None

    def enhance_contrast(self, ds, coef_a, coef_b):
        """
        Apply contrast enhancement while preserving DICOM properties
        """
        # Get original pixel data
        original_pixels = ds.pixel_array.astype(float)
        
        # Store original data type
        original_dtype = ds.pixel_array.dtype
        
        # Get image properties
        if hasattr(ds, 'RescaleSlope'):
            rescale_slope = float(ds.RescaleSlope)
        else:
            rescale_slope = 1.0
            
        if hasattr(ds, 'RescaleIntercept'):
            rescale_intercept = float(ds.RescaleIntercept)
        else:
            rescale_intercept = 0.0
            
        # Convert stored pixels to actual HU values if needed
        hu_values = original_pixels * rescale_slope + rescale_intercept
        
        # Apply contrast enhancement equation
        enhanced_hu = coef_a * hu_values - coef_b
        
        # Convert back to stored pixel values
        if rescale_slope != 1.0 or rescale_intercept != 0.0:
            enhanced_pixels = (enhanced_hu - rescale_intercept) / rescale_slope
        else:
            enhanced_pixels = enhanced_hu
            
        # Round to nearest integer
        enhanced_pixels = np.round(enhanced_pixels)
        
        # Clip to valid range for the data type
        info = np.iinfo(original_dtype)
        enhanced_pixels = np.clip(enhanced_pixels, info.min, info.max)
        
        # Convert back to original data type
        enhanced_pixels = enhanced_pixels.astype(original_dtype)
        
        return enhanced_pixels

    def log_progress(self, message):
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update()

    def process_images(self):
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Error", "Please select both input and output folders")
            return

        valid, coef_a, coef_b = self.validate_coefficients()
        if not valid:
            return

        try:
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)

            self.progress_text.delete(1.0, tk.END)
            self.log_progress(f"Using equation: y = {coef_a}x - {coef_b}")
            
            dicom_files = [f for f in os.listdir(self.input_folder) if f.endswith('.dcm')]
            
            if not dicom_files:
                self.log_progress("No DICOM files found in the input folder!")
                return

            total_files = len(dicom_files)
            processed_files = 0

            for filename in dicom_files:
                try:
                    input_path = os.path.join(self.input_folder, filename)
                    output_path = os.path.join(self.output_folder, filename)
                    
                    # Read DICOM file
                    ds = pydicom.dcmread(input_path)
                    
                    # Create a copy of the dataset to preserve all metadata
                    ds_output = pydicom.Dataset()
                    ds_output = ds.copy()
                    
                    # Apply contrast enhancement
                    enhanced_pixels = self.enhance_contrast(ds, coef_a, coef_b)
                    
                    # Update pixel data while preserving metadata
                    ds_output.PixelData = enhanced_pixels.tobytes()
                    
                    # Preserve or update important DICOM tags
                    ds_output.Rows = ds.Rows
                    ds_output.Columns = ds.Columns
                    ds_output.BitsAllocated = ds.BitsAllocated
                    ds_output.BitsStored = ds.BitsStored
                    ds_output.HighBit = ds.HighBit
                    ds_output.PixelRepresentation = ds.PixelRepresentation
                    ds_output.SamplesPerPixel = ds.SamplesPerPixel
                    ds_output.PhotometricInterpretation = ds.PhotometricInterpretation
                    
                    # Add processing information
                    ds_output.add_new(0x00071001, 'LO', 'Contrast enhanced')
                    ds_output.add_new(0x00071002, 'LO', f'y={coef_a}x-{coef_b}')
                    
                    # Save processed image
                    ds_output.save_as(output_path)
                    
                    processed_files += 1
                    self.log_progress(f"Processed: {filename} ({processed_files}/{total_files})")
                    
                    # Debug information for first pixel values
                    if processed_files == 1:
                        sample_coords = (100, 100)
                        original_val = ds.pixel_array[sample_coords]
                        enhanced_val = enhanced_pixels[sample_coords]
                        self.log_progress(f"\nDebug - Pixel at {sample_coords}:")
                        self.log_progress(f"Original value: {original_val}")
                        self.log_progress(f"Enhanced value: {enhanced_val}")
                        self.log_progress(f"Theoretical value: {coef_a * float(original_val) - coef_b}")
                    
                except Exception as e:
                    self.log_progress(f"Error processing {filename}: {str(e)}")
                    continue

            self.log_progress("\nProcessing completed!")
            messagebox.showinfo("Success", "Processing completed successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DicomEnhancerGUI(root)
    root.mainloop()
