import pydicom
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from skimage.exposure import equalize_adapthist

class DicomEnhancerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DICOM Contrast Enhancement with CLAHE")
        
        # Set window size and position
        window_width = 750
        window_height = 650
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Initialize variables
        self.input_folder = ""
        self.base_output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        
        # Create GUI elements
        self.create_widgets()
        
        # Set up method change callback
        self.method_var.trace_add("write", self.on_method_change)

    def on_method_change(self, *args):
        input_folder = self.input_path_var.get()
        method = self.method_var.get()
        if input_folder:
            output_folder = os.path.join(
                os.path.dirname(input_folder),
                "output",
                method
            )
            self.output_folder = output_folder
            self.output_path_var.set(output_folder)
        else:
            self.output_folder = ""
            self.output_path_var.set("")

    def create_widgets(self):
        # Enhancement method selection frame
        method_frame = tk.LabelFrame(self.root, text="Enhancement Method Selection", pady=10, padx=10)
        method_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.method_var = tk.StringVar(value="linear_only")
        
        tk.Radiobutton(method_frame, text="Linear Enhancement Only", 
                      variable=self.method_var, value="linear_only").pack(anchor=tk.W)
        tk.Radiobutton(method_frame, text="CLAHE Only", 
                      variable=self.method_var, value="clahe_only").pack(anchor=tk.W)
        tk.Radiobutton(method_frame, text="Linear Enhancement → CLAHE", 
                      variable=self.method_var, value="linear_then_clahe").pack(anchor=tk.W)
        tk.Radiobutton(method_frame, text="CLAHE → Linear Enhancement", 
                      variable=self.method_var, value="clahe_then_linear").pack(anchor=tk.W)

        # Linear equation frame
        equation_frame = tk.LabelFrame(self.root, text="Linear Contrast Enhancement: y = ax - b", pady=10, padx=10)
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

        # CLAHE parameters frame
        clahe_frame = tk.LabelFrame(self.root, text="CLAHE Parameters", pady=10, padx=10)
        clahe_frame.pack(fill=tk.X, padx=20, pady=10)
        
        clip_limit_frame = tk.Frame(clahe_frame)
        clip_limit_frame.pack(fill=tk.X, pady=5)
        tk.Label(clip_limit_frame, text="Clip Limit:").pack(side=tk.LEFT)
        self.clip_limit_var = tk.StringVar(value="0.01")
        tk.Entry(clip_limit_frame, textvariable=self.clip_limit_var, width=10).pack(side=tk.LEFT, padx=5)
        tk.Label(clip_limit_frame, text="(Higher values = more contrast)").pack(side=tk.LEFT, padx=5)

        # Input folder selection
        input_frame = tk.LabelFrame(self.root, text="Folder Selection", pady=10, padx=10)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        input_folder_frame = tk.Frame(input_frame)
        input_folder_frame.pack(fill=tk.X, pady=5)
        tk.Label(input_folder_frame, text="Input Folder:").pack(side=tk.LEFT)
        self.input_path_var = tk.StringVar()
        tk.Entry(input_folder_frame, textvariable=self.input_path_var, width=50).pack(side=tk.LEFT, padx=5)
        tk.Button(input_folder_frame, text="Browse", command=self.select_input_folder).pack(side=tk.LEFT)

        # Output folder selection (read-only)
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
        
        self.progress_text = tk.Text(progress_frame, height=8, width=60)
        self.progress_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def select_input_folder(self):
        self.input_folder = filedialog.askdirectory(title="Select Input Folder")
        self.input_path_var.set(self.input_folder)
        # Update output folder based on current method
        self.on_method_change()

    def select_output_folder(self):
        output_folder = filedialog.askdirectory(title="Select Output Folder")
        if output_folder:
            self.output_path_var.set(output_folder)
            self.output_folder = output_folder

    def get_current_parameters(self):
        """Get current values of all parameters"""
        return {
            'method': self.method_var.get(),
            'coef_a': float(self.coef_a_var.get()),
            'coef_b': float(self.coef_b_var.get()),
            'clip_limit': float(self.clip_limit_var.get()),
            'input_folder': self.input_path_var.get(),
            'output_folder': self.output_path_var.get()
        }

    def normalize_for_clahe(self, pixel_array):
        """
        Normalize pixel array to [0, 1] range for CLAHE processing
        Returns normalized array and scaling parameters for restoration
        """
        min_val = np.min(pixel_array)
        max_val = np.max(pixel_array)
        
        # Avoid division by zero
        if max_val == min_val:
            return pixel_array.astype(np.float64), min_val, max_val
        
        normalized = (pixel_array.astype(np.float64) - min_val) / (max_val - min_val)
        return normalized, min_val, max_val

    def denormalize_from_clahe(self, normalized_array, min_val, max_val, original_dtype):
        """
        Convert normalized array back to original scale and data type
        """
        if max_val == min_val:
            return normalized_array.astype(original_dtype)
        
        # Scale back to original range
        scaled = normalized_array * (max_val - min_val) + min_val
        
        # Round to nearest integer and clip to valid range
        scaled = np.round(scaled)
        
        # Get valid range for the data type
        info = np.iinfo(original_dtype)
        scaled = np.clip(scaled, info.min, info.max)
        
        return scaled.astype(original_dtype)

    def apply_clahe(self, pixel_array, clip_limit):
        """
        Apply CLAHE to pixel array while preserving data type and range
        """
        original_dtype = pixel_array.dtype
        
        # Normalize to [0, 1] for CLAHE
        normalized, min_val, max_val = self.normalize_for_clahe(pixel_array)
        
        # Apply CLAHE
        enhanced_normalized = equalize_adapthist(normalized, clip_limit=clip_limit)
        
        # Convert back to original scale and data type
        enhanced_pixels = self.denormalize_from_clahe(enhanced_normalized, min_val, max_val, original_dtype)
        
        return enhanced_pixels

    def apply_linear_enhancement(self, pixel_array, coef_a, coef_b, ds):
        """
        Apply linear contrast enhancement while preserving DICOM properties
        """
        # Get original pixel data
        original_pixels = pixel_array.astype(float)
        
        # Store original data type
        original_dtype = pixel_array.dtype
        
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

    def enhance_contrast(self, ds, coef_a, coef_b, clip_limit, method):
        """
        Apply contrast enhancement based on selected method
        """
        original_pixels = ds.pixel_array
        
        if method == "linear_only":
            enhanced_pixels = self.apply_linear_enhancement(original_pixels, coef_a, coef_b, ds)
            
        elif method == "clahe_only":
            enhanced_pixels = self.apply_clahe(original_pixels, clip_limit)
            
        elif method == "linear_then_clahe":
            # Apply linear enhancement first
            linear_enhanced = self.apply_linear_enhancement(original_pixels, coef_a, coef_b, ds)
            # Then apply CLAHE
            enhanced_pixels = self.apply_clahe(linear_enhanced, clip_limit)
            
        elif method == "clahe_then_linear":
            # Apply CLAHE first
            clahe_enhanced = self.apply_clahe(original_pixels, clip_limit)
            # Create a temporary dataset copy for linear enhancement
            temp_ds = ds.copy()
            temp_ds.PixelData = clahe_enhanced.tobytes()
            # Then apply linear enhancement
            enhanced_pixels = self.apply_linear_enhancement(clahe_enhanced, coef_a, coef_b, temp_ds)
        
        return enhanced_pixels

    def log_progress(self, message):
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.see(tk.END)
        self.root.update()

    def reset_progress(self):
        """Clear the progress text and update the GUI"""
        self.progress_text.delete(1.0, tk.END)
        self.root.update()

    def process_images(self):
        # Get current parameters
        params = self.get_current_parameters()
        
        if not params['input_folder']:
            messagebox.showerror("Error", "Please select input folder")
            return

        try:
            # Create output directory if it doesn't exist
            if not os.path.exists(params['output_folder']):
                os.makedirs(params['output_folder'])
            else:
                # Clear existing files in output directory
                for file in os.listdir(params['output_folder']):
                    if file.endswith('.dcm'):
                        os.remove(os.path.join(params['output_folder'], file))

            self.reset_progress()
            
            # Log processing parameters
            if params['method'] == "linear_only":
                self.log_progress(f"Using Linear Enhancement: y = {params['coef_a']}x - {params['coef_b']}")
            elif params['method'] == "clahe_only":
                self.log_progress(f"Using CLAHE with clip limit: {params['clip_limit']}")
            elif params['method'] == "linear_then_clahe":
                self.log_progress(f"Using Linear → CLAHE: y = {params['coef_a']}x - {params['coef_b']}, clip limit: {params['clip_limit']}")
            elif params['method'] == "clahe_then_linear":
                self.log_progress(f"Using CLAHE → Linear: clip limit: {params['clip_limit']}, y = {params['coef_a']}x - {params['coef_b']}")
            
            dicom_files = [f for f in os.listdir(params['input_folder']) if f.endswith('.dcm')]
            
            if not dicom_files:
                self.log_progress("No DICOM files found in the input folder!")
                return

            total_files = len(dicom_files)
            processed_files = 0

            for filename in dicom_files:
                try:
                    input_path = os.path.join(params['input_folder'], filename)
                    output_path = os.path.join(params['output_folder'], filename)
                    
                    # Read DICOM file
                    ds = pydicom.dcmread(input_path)
                    
                    # Create a copy of the dataset to preserve all metadata
                    ds_output = ds.copy()
                    
                    # Apply contrast enhancement based on selected method
                    enhanced_pixels = self.enhance_contrast(ds, params['coef_a'], params['coef_b'], 
                                                         params['clip_limit'], params['method'])
                    
                    # Update pixel data while preserving metadata
                    ds_output.PixelData = enhanced_pixels.tobytes()
                    
                    # Preserve important DICOM tags
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
                    if params['method'] == "linear_only":
                        ds_output.add_new(0x00071002, 'LO', f'Linear: y={params["coef_a"]}x-{params["coef_b"]}')
                    elif params['method'] == "clahe_only":
                        ds_output.add_new(0x00071002, 'LO', f'CLAHE: clip={params["clip_limit"]}')
                    elif params['method'] == "linear_then_clahe":
                        ds_output.add_new(0x00071002, 'LO', f'Linear then CLAHE: y={params["coef_a"]}x-{params["coef_b"]}, clip={params["clip_limit"]}')
                    elif params['method'] == "clahe_then_linear":
                        ds_output.add_new(0x00071002, 'LO', f'CLAHE then Linear: clip={params["clip_limit"]}, y={params["coef_a"]}x-{params["coef_b"]}')
                    
                    # Save processed image
                    ds_output.save_as(output_path)
                    
                    processed_files += 1
                    self.log_progress(f"Processed: {filename} ({processed_files}/{total_files})")
                    
                    # Debug information for first processed file
                    if processed_files == 1:
                        sample_coords = (min(100, ds.Rows-1), min(100, ds.Columns-1))
                        original_val = ds.pixel_array[sample_coords]
                        enhanced_val = enhanced_pixels[sample_coords]
                        self.log_progress(f"\nDebug - Pixel at {sample_coords}:")
                        self.log_progress(f"Original value: {original_val}")
                        self.log_progress(f"Enhanced value: {enhanced_val}")
                    
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
