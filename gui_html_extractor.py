import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import re
from pathlib import Path
import sys
import threading
from datetime import datetime
import json
import shutil

try:
    import sass
    SASS_AVAILABLE = True
except ImportError:
    SASS_AVAILABLE = False

class HTMLExtractorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HTML JS/CSS/Sass Extractor v2.1 - Enhanced")
        self.geometry("1000x800")
        
        # Configure window icon and styling
        self.configure(bg='#f0f0f0')
        
        # Center the window
        self.center_window()
        
        # Configure window to be resizable
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        
        # Variables
        self.html_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.convert_sass = tk.BooleanVar(value=True)
        self.minify_output = tk.BooleanVar(value=False)
        self.preserve_comments = tk.BooleanVar(value=True)
        self.create_backup = tk.BooleanVar(value=True)
        self.extract_inline_styles = tk.BooleanVar(value=True)
        self.batch_mode = tk.BooleanVar(value=False)
        self.create_project_folder = tk.BooleanVar(value=True)
        self.combine_files = tk.BooleanVar(value=True)
        
        # Progress tracking
        self.progress_var = tk.DoubleVar()
        self.is_extracting = False
        
        # Build the GUI
        self._build_widgets()
        
        # Load previous settings
        self._load_settings()
        
        # Set focus to the window
        self.focus_force()
        
        # Bind cleanup on close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = 1000
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _build_widgets(self):
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main extraction tab
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Extraction")
        
        # Settings tab
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        self._build_main_tab(main_frame)
        self._build_settings_tab(settings_frame)
        
    def _build_main_tab(self, parent):
        # Main container with padding
        main_container = ttk.Frame(parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # File selection frame with improved styling
        file_frame = ttk.LabelFrame(main_container, text="File Selection", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # HTML file selection
        ttk.Label(file_frame, text="HTML file:").grid(row=0, column=0, sticky=tk.W, pady=5)
        html_entry = ttk.Entry(file_frame, textvariable=self.html_path, width=60)
        html_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 10), pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_html, width=12).grid(row=0, column=2, pady=5)
        
        # Batch mode checkbox
        batch_cb = ttk.Checkbutton(file_frame, text="Batch mode (select folder)", variable=self.batch_mode)
        batch_cb.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Output directory selection
        ttk.Label(file_frame, text="Output directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        output_entry = ttk.Entry(file_frame, textvariable=self.output_dir, width=60)
        output_entry.grid(row=2, column=1, sticky=tk.EW, padx=(10, 10), pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output, width=12).grid(row=2, column=2, pady=5)

        # Enhanced options frame
        enhanced_options_frame = ttk.LabelFrame(main_container, text="Enhanced Output Options", padding="10")
        enhanced_options_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Checkbutton(enhanced_options_frame, text="Create project folder for each HTML file", 
                       variable=self.create_project_folder).pack(anchor=tk.W, pady=2)
        
        ttk.Checkbutton(enhanced_options_frame, text="Combine multiple scripts/styles into single files", 
                       variable=self.combine_files).pack(anchor=tk.W, pady=2)

        # Quick options frame
        quick_options_frame = ttk.LabelFrame(main_container, text="Quick Options", padding="10")
        quick_options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create a grid for options
        options_grid = ttk.Frame(quick_options_frame)
        options_grid.pack(fill=tk.X)
        
        ttk.Checkbutton(options_grid, text="Convert Sass to CSS", 
                       variable=self.convert_sass,
                       state=tk.NORMAL if SASS_AVAILABLE else tk.DISABLED).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        ttk.Checkbutton(options_grid, text="Create backup", 
                       variable=self.create_backup).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Checkbutton(options_grid, text="Extract inline styles", 
                       variable=self.extract_inline_styles).grid(row=1, column=0, sticky=tk.W, padx=(0, 20))
        
        ttk.Checkbutton(options_grid, text="Preserve comments", 
                       variable=self.preserve_comments).grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        if not SASS_AVAILABLE:
            sass_warning = ttk.Label(quick_options_frame, 
                                   text="⚠ libsass not installed - install with: pip install libsass", 
                                   foreground="orange")
            sass_warning.pack(anchor=tk.W, pady=(5, 0))

        # Progress frame
        progress_frame = ttk.Frame(main_container)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Control buttons frame with better styling
        btn_frame = ttk.Frame(main_container)
        btn_frame.pack(pady=10)
        
        self.extract_btn = ttk.Button(btn_frame, text="🚀 Start Extraction", 
                                     command=self.run_extraction_threaded, width=20)
        self.extract_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹ Stop", 
                                  command=self.stop_extraction, width=12, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="📋 Clear Log", 
                  command=self.clear_log, width=12).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="💾 Save Log", 
                  command=self.save_log, width=12).pack(side=tk.LEFT, padx=5)

        # Log area frame with improved styling
        log_frame = ttk.LabelFrame(main_container, text="Extraction Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text area with syntax highlighting capability
        self.log_area = scrolledtext.ScrolledText(log_frame, height=20, width=120, 
                                                 state='normal', wrap=tk.WORD,
                                                 font=("Consolas", 9) if sys.platform == "win32" else ("Monaco", 9),
                                                 bg='#1e1e1e', fg='#d4d4d4', insertbackground='white')
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags for colored output
        self.log_area.tag_config("success", foreground="#4CAF50")
        self.log_area.tag_config("warning", foreground="#FF9800")
        self.log_area.tag_config("error", foreground="#F44336")
        self.log_area.tag_config("info", foreground="#2196F3")
        self.log_area.tag_config("header", foreground="#9C27B0", font=("Consolas", 10, "bold"))
        self.log_area.tag_config("folder", foreground="#FFC107", font=("Consolas", 9, "bold"))
        
        # Status bar with more information
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_bar = ttk.Label(status_frame, text="Ready • Select HTML file to begin", 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.time_label = ttk.Label(status_frame, text="")
        self.time_label.pack(side=tk.RIGHT, padx=(10, 0))

    def _build_settings_tab(self, parent):
        # Settings container
        settings_container = ttk.Frame(parent)
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # File organization frame
        org_frame = ttk.LabelFrame(settings_container, text="File Organization", padding="15")
        org_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Checkbutton(org_frame, text="Create project folder for each HTML file", 
                       variable=self.create_project_folder).pack(anchor=tk.W, pady=5)
        
        ttk.Checkbutton(org_frame, text="Combine multiple scripts/styles into single files", 
                       variable=self.combine_files).pack(anchor=tk.W, pady=5)
        
        # File naming explanation
        naming_info = ttk.Label(org_frame, text="Standard filenames: index.html, style.css, script.js", 
                               foreground="gray")
        naming_info.pack(anchor=tk.W, pady=(10, 0))
        
        # Advanced options frame
        advanced_frame = ttk.LabelFrame(settings_container, text="Advanced Options", padding="15")
        advanced_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Checkbutton(advanced_frame, text="Minify extracted files (removes whitespace)", 
                       variable=self.minify_output).pack(anchor=tk.W, pady=5)
        
        ttk.Checkbutton(advanced_frame, text="Preserve comments in extracted files", 
                       variable=self.preserve_comments).pack(anchor=tk.W, pady=5)
        
        ttk.Checkbutton(advanced_frame, text="Extract inline styles to separate CSS file", 
                       variable=self.extract_inline_styles).pack(anchor=tk.W, pady=5)
        
        ttk.Checkbutton(advanced_frame, text="Create backup of original HTML file", 
                       variable=self.create_backup).pack(anchor=tk.W, pady=5)
        
        # Reset settings button
        ttk.Button(settings_container, text="Reset to Defaults", 
                  command=self.reset_settings).pack(pady=20)

    def browse_html(self):
        """Browse for HTML file or folder"""
        if self.batch_mode.get():
            dir_path = filedialog.askdirectory(
                title="Select Folder with HTML Files",
                initialdir=os.getcwd()
            )
            if dir_path:
                self.html_path.set(dir_path)
                html_files = list(Path(dir_path).glob("*.html")) + list(Path(dir_path).glob("*.htm"))
                self.log(f"Selected folder: {dir_path}", "info")
                self.log(f"Found {len(html_files)} HTML files", "info")
        else:
            file_types = [
                ("HTML files", "*.html *.htm"),
                ("All files", "*.*")
            ]
            file_path = filedialog.askopenfilename(
                title="Select HTML File",
                filetypes=file_types,
                initialdir=os.getcwd()
            )
            if file_path:
                self.html_path.set(file_path)
                self.log(f"Selected HTML file: {os.path.basename(file_path)}", "info")

    def browse_output(self):
        """Browse for output directory"""
        dir_path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=os.getcwd()
        )
        if dir_path:
            self.output_dir.set(dir_path)
            self.log(f"Selected output directory: {dir_path}", "info")

    def clear_log(self):
        """Clear the log area"""
        self.log_area.delete(1.0, tk.END)
        self.update_status("Log cleared")

    def save_log(self):
        """Save log to file"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Log File",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                content = self.log_area.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"HTML Extractor Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(content)
                messagebox.showinfo("Success", f"Log saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")

    def log(self, msg, tag="normal"):
        """Add message to log area with optional color tag"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {msg}\n"
        
        self.log_area.insert(tk.END, formatted_msg, tag)
        self.log_area.see(tk.END)
        self.update_idletasks()

    def update_status(self, status):
        """Update status bar"""
        self.status_bar.config(text=status)
        self.update_idletasks()

    def update_progress(self, value, text=""):
        """Update progress bar and label"""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=text)
        self.update_idletasks()

    def run_extraction_threaded(self):
        """Run extraction in a separate thread"""
        if self.is_extracting:
            return
            
        # Validation
        html_path = self.html_path.get().strip()
        out_dir = self.output_dir.get().strip()
        
        if not html_path:
            messagebox.showwarning("No HTML file", "Please select an HTML file or folder.")
            return
        
        if not out_dir:
            messagebox.showwarning("No Output Directory", "Please select an output directory.")
            return
        
        # Start extraction in thread
        self.is_extracting = True
        self.extract_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        self.extraction_thread = threading.Thread(target=self._run_extraction_worker, 
                                                 args=(html_path, out_dir), daemon=True)
        self.extraction_thread.start()

    def _run_extraction_worker(self, html_path, out_dir):
        """Worker method for extraction"""
        try:
            start_time = datetime.now()
            self.clear_log()
            self.update_status("Extracting...")
            self.update_progress(0, "Initializing...")
            
            # Save current settings
            self._save_settings()
            
            if self.batch_mode.get() and os.path.isdir(html_path):
                self._extract_batch(html_path, out_dir)
            else:
                self._extract_single_file(html_path, out_dir)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.log(f"✅ Extraction completed successfully in {duration:.2f} seconds", "success")
            self.update_status("Extraction completed successfully")
            self.update_progress(100, "Complete")
            
            # Show completion dialog in main thread
            self.after(0, lambda: messagebox.showinfo("Success", 
                                                     f"Extraction completed successfully!\nTime taken: {duration:.2f} seconds"))
            
        except Exception as e:
            error_msg = f"Error during extraction: {str(e)}"
            self.log(error_msg, "error")
            self.update_status("Extraction failed")
            self.update_progress(0, "Failed")
            self.after(0, lambda: messagebox.showerror("Extraction Error", error_msg))
        finally:
            self.is_extracting = False
            self.after(0, self._reset_ui_state)

    def _extract_batch(self, folder_path, out_dir):
        """Extract multiple HTML files"""
        html_files = list(Path(folder_path).glob("*.html")) + list(Path(folder_path).glob("*.htm"))
        
        if not html_files:
            raise ValueError("No HTML files found in the selected folder")
        
        self.log(f"🔄 Starting batch extraction of {len(html_files)} files", "header")
        
        for i, html_file in enumerate(html_files):
            if not self.is_extracting:  # Check if stopped
                break
                
            progress = (i / len(html_files)) * 100
            self.update_progress(progress, f"Processing {html_file.name}")
            
            self.log(f"\n📄 Processing: {html_file.name}", "info")
            
            try:
                self.extract_html(str(html_file), out_dir)
            except Exception as e:
                self.log(f"❌ Failed to process {html_file.name}: {e}", "error")
                continue

    def _extract_single_file(self, html_file, out_dir):
        """Extract single HTML file"""
        if not os.path.isfile(html_file):
            raise ValueError(f"The file '{html_file}' does not exist.")
            
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            self.log(f"📁 Created output directory: {out_dir}", "info")
        
        self.extract_html(html_file, out_dir)

    def stop_extraction(self):
        """Stop the extraction process"""
        self.is_extracting = False
        self.log("⏹ Extraction stopped by user", "warning")
        self.update_status("Extraction stopped")

    def _reset_ui_state(self):
        """Reset UI state after extraction"""
        self.extract_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def extract_html(self, html_file, base_out_dir):
        """Enhanced HTML extraction with standardized file structure"""
        self.log(f"🚀 Starting extraction from: {os.path.basename(html_file)}", "header")
        
        # Read HTML file with better encoding handling
        html_content = self._read_html_file(html_file)
        base_name = Path(html_file).stem
        
        # Create project folder if requested
        if self.create_project_folder.get():
            project_dir = os.path.join(base_out_dir, f"{base_name}_extracted")
            os.makedirs(project_dir, exist_ok=True)
            out_dir = project_dir
            self.log(f"📁 Created project folder: {os.path.basename(project_dir)}", "folder")
        else:
            out_dir = base_out_dir
        
        self.log(f"📂 Output directory: {out_dir}", "info")
        self.log("-" * 60)
        
        # Create backup if requested
        if self.create_backup.get():
            backup_path = os.path.join(out_dir, f"{base_name}_original.html")
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.log(f"💾 Created backup: {os.path.basename(backup_path)}", "info")
        
        # Initialize containers for extracted content
        all_js_content = []
        all_css_content = []
        inline_styles_content = []
        new_scripts = []
        new_links = []
        
        # Extract inline styles if requested
        if self.extract_inline_styles.get():
            html_content, inline_styles = self._extract_inline_styles_content(html_content)
            if inline_styles:
                inline_styles_content.extend(inline_styles)
                self.log(f"✅ Extracted {len(inline_styles)} inline styles", "success")
        
        # Extract script blocks
        html_content, extracted_js = self._extract_scripts_content(html_content)
        if extracted_js:
            all_js_content.extend(extracted_js)
            self.log(f"✅ Extracted {len(extracted_js)} script blocks", "success")
        
        # Extract style blocks
        html_content, extracted_css, extracted_sass = self._extract_styles_content(html_content)
        if extracted_css:
            all_css_content.extend(extracted_css)
            self.log(f"✅ Extracted {len(extracted_css)} CSS blocks", "success")
        if extracted_sass:
            self.log(f"✅ Extracted {len(extracted_sass)} Sass blocks", "success")
        
        # Save extracted files with standard names
        files_created = self._save_extracted_files(out_dir, all_js_content, all_css_content, 
                                                  inline_styles_content, extracted_sass)
        
        # Update HTML with new references
        html_content = self._update_html_with_standard_refs(html_content, files_created)
        
        # Save updated HTML as index.html
        self._save_index_html(html_content, out_dir)
        
        # Generate summary
        self._log_extraction_summary_enhanced(files_created, out_dir, base_name)

    def _read_html_file(self, html_file):
        """Read HTML file with encoding detection"""
        encodings = ['utf-8', 'iso-8859-1', 'cp1252', 'ascii']
        
        for encoding in encodings:
            try:
                with open(html_file, 'r', encoding=encoding) as f:
                    content = f.read()
                if encoding != 'utf-8':
                    self.log(f"⚠ File read with {encoding} encoding", "warning")
                return content
            except UnicodeDecodeError:
                continue
        
        raise Exception("Cannot decode HTML file with any supported encoding")

    def _extract_inline_styles_content(self, html_content):
        """Extract inline styles and return cleaned HTML and styles list"""
        inline_styles = re.findall(r'style\s*=\s*["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        
        if not inline_styles:
            return html_content, []
        
        # Clean styles and remove from HTML
        cleaned_styles = []
        for style in inline_styles:
            if style.strip():
                cleaned_styles.append(style.strip())
                # Remove inline style attributes
                html_content = re.sub(r'\s*style\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        return html_content, cleaned_styles

    def _extract_scripts_content(self, html_content):
        """Extract JavaScript content and return cleaned HTML and scripts list"""
        scripts = []
        
        def script_repl(match):
            full_tag = match.group(0)
            attributes = match.group(1)
            js_code = match.group(2)
            
            # Skip external scripts
            if re.search(r'src\s*=', attributes, re.IGNORECASE):
                return full_tag
            
            # Skip empty scripts
            if not js_code.strip():
                return full_tag
            
            scripts.append(self._process_javascript(js_code))
            return ''  # Remove the script tag
        
        cleaned_html = re.sub(r'<script([^>]*?)>(.*?)</script>', script_repl, html_content, 
                             flags=re.IGNORECASE | re.DOTALL)
        
        return cleaned_html, scripts

    def _extract_styles_content(self, html_content):
        """Extract CSS/Sass content and return cleaned HTML and styles lists"""
        css_styles = []
        sass_styles = []
        
        def style_repl(match):
            css_code = match.group(1)
            
            if not css_code.strip():
                return match.group(0)
            
            if self._detect_sass(css_code):
                sass_styles.append(self._process_stylesheet(css_code))
            else:
                css_styles.append(self._process_stylesheet(css_code))
            
            return ''  # Remove the style tag
        
        cleaned_html = re.sub(r'<style[^>]*?>(.*?)</style>', style_repl, html_content, 
                             flags=re.IGNORECASE | re.DOTALL)
        
        return cleaned_html, css_styles, sass_styles

    def _save_extracted_files(self, out_dir, js_content, css_content, inline_styles, sass_content):
        """Save extracted content to standardized files"""
        files_created = {
            'js': False,
            'css': False,
            'sass': False
        }
        
        # Combine and save JavaScript
        if js_content:
            combined_js = '\n\n'.join(js_content)
            js_path = os.path.join(out_dir, 'script.js')
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(f"// Combined JavaScript - Generated by HTML Extractor\n// {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(combined_js)
            files_created['js'] = True
            self.log(f"📄 Created: script.js", "success")
        
        # Combine and save CSS (including inline styles)
        all_css = css_content + inline_styles
        if all_css:
            combined_css = '\n\n'.join(all_css)
            css_path = os.path.join(out_dir, 'style.css')
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(f"/* Combined CSS - Generated by HTML Extractor */\n/* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} */\n\n")
                f.write(combined_css)
            files_created['css'] = True
            self.log(f"📄 Created: style.css", "success")
        
        # Save Sass if present
        if sass_content:
            combined_sass = '\n\n'.join(sass_content)
            sass_path = os.path.join(out_dir, 'style.scss')
            with open(sass_path, 'w', encoding='utf-8') as f:
                f.write(f"// Combined Sass - Generated by HTML Extractor\n// {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(combined_sass)
            files_created['sass'] = True
            self.log(f"📄 Created: style.scss", "success")
            
            # Convert to CSS if enabled
            if self.convert_sass.get() and SASS_AVAILABLE:
                try:
                    compiled = sass.compile(filename=sass_path, 
                                          output_style='compressed' if self.minify_output.get() else 'expanded')
                    css_path = os.path.join(out_dir, 'style.css')
                    with open(css_path, 'w', encoding='utf-8') as f:
                        f.write(f"/* Compiled from Sass - Generated by HTML Extractor */\n/* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} */\n\n")
                        f.write(compiled)
                    files_created['css'] = True
                    self.log(f"✅ Compiled Sass → style.css", "success")
                except Exception as e:
                    self.log(f"❌ Failed to compile Sass: {e}", "error")
        
        return files_created

    def _update_html_with_standard_refs(self, html_content, files_created):
        """Update HTML with references to standard files"""
        # Add CSS link if CSS was created
        if files_created['css']:
            head_match = re.search(r'<head[^>]*>', html_content, re.IGNORECASE)
            if head_match:
                insert_pos = head_match.end()
                css_link = '\n    <link rel="stylesheet" href="style.css">'
                html_content = html_content[:insert_pos] + css_link + html_content[insert_pos:]
                self.log(f"✅ Added CSS link to <head>", "success")
        
        # Add script tag if JS was created
        if files_created['js']:
            body_match = re.search(r'</body>', html_content, re.IGNORECASE)
            if body_match:
                insert_pos = body_match.start()
                script_tag = '\n    <script src="script.js"></script>\n'
                html_content = html_content[:insert_pos] + script_tag + html_content[insert_pos:]
                self.log(f"✅ Added script tag before </body>", "success")
            else:
                # Append at end if no </body>
                script_tag = '\n<script src="script.js"></script>'
                html_content += script_tag
                self.log(f"✅ Added script tag at end of file", "success")
        
        return html_content

    def _save_index_html(self, html_content, out_dir):
        """Save the updated HTML as index.html"""
        index_path = os.path.join(out_dir, 'index.html')
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.log(f"📄 Created: index.html", "success")
        except Exception as e:
            raise Exception(f"Failed to save index.html: {e}")

    def _detect_sass(self, css_code):
        """Enhanced Sass detection"""
        sass_patterns = [
            r'\$[\w-]+\s*:',           # Variables
            r'@mixin\s+[\w-]+',        # Mixins
            r'@include\s+[\w-]+',      # Include
            r'@extend\s+',             # Extend
            r'@import\s+["\']',        # Import
            r'&\s*[:\w\[\]]',          # Parent selector
            r'^\s*[\w-]+\s*{[^}]*[\w-]+\s*{',  # Nested rules
            r'@if\s+',                 # Conditionals
            r'@for\s+',                # Loops
            r'@each\s+',               # Each loops
            r'@function\s+',           # Functions
        ]
        
        for pattern in sass_patterns:
            if re.search(pattern, css_code, re.MULTILINE):
                return True
        return False

    def _process_javascript(self, js_code):
        """Process JavaScript code (minify if requested, preserve comments)"""
        code = js_code.strip()
        
        if not self.preserve_comments.get():
            # Remove single-line comments
            code = re.sub(r'//.*%, ''', code, flags=re.MULTILINE)
            # Remove multi-line comments
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        if self.minify_output.get():
            # Basic minification (remove extra whitespace)
            code = re.sub(r'\s+', ' ', code)
            code = re.sub(r';\s*}', '}', code)
            code = re.sub(r'{\s*', '{', code)
            code = code.strip()
        
        return code

    def _process_stylesheet(self, css_code):
        """Process CSS/Sass code (minify if requested, preserve comments)"""
        code = css_code.strip()
        
        if not self.preserve_comments.get():
            # Remove CSS comments
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        if self.minify_output.get():
            # Basic CSS minification
            code = re.sub(r'\s+', ' ', code)
            code = re.sub(r';\s*}', '}', code)
            code = re.sub(r'{\s*', '{', code)
            code = re.sub(r':\s*', ':', code)
            code = re.sub(r';\s*', ';', code)
            code = code.strip()
        
        return code

    def _log_extraction_summary_enhanced(self, files_created, out_dir, base_name):
        """Log enhanced extraction summary"""
        self.log("-" * 60)
        self.log("📊 EXTRACTION SUMMARY:", "header")
        
        created_files = []
        if files_created['js']:
            created_files.append("script.js")
        if files_created['css']:
            created_files.append("style.css")
        if files_created['sass']:
            created_files.append("style.scss")
        created_files.append("index.html")
        
        self.log(f"   📁 Project folder: {os.path.basename(out_dir)}", "folder")
        self.log(f"   📄 Files created: {', '.join(created_files)}")
        self.log(f"   🏗️ Structure: Standard web project layout")
        
        if self.create_backup.get():
            self.log(f"   💾 Backup: {base_name}_original.html")
        
        total_files = len(created_files)
        if self.create_backup.get():
            total_files += 1
        
        self.log(f"   📊 Total files: {total_files}")
        self.log("   ✨ Ready for development!")

    def _save_settings(self):
        """Save current settings to file"""
        settings = {
            'convert_sass': self.convert_sass.get(),
            'minify_output': self.minify_output.get(),
            'preserve_comments': self.preserve_comments.get(),
            'create_backup': self.create_backup.get(),
            'extract_inline_styles': self.extract_inline_styles.get(),
            'create_project_folder': self.create_project_folder.get(),
            'combine_files': self.combine_files.get(),
            'last_output_dir': self.output_dir.get()
        }
        
        try:
            settings_path = os.path.join(os.path.expanduser("~"), ".html_extractor_settings.json")
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:
            pass  # Fail silently if can't save settings

    def _load_settings(self):
        """Load settings from file"""
        try:
            settings_path = os.path.join(os.path.expanduser("~"), ".html_extractor_settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                
                self.convert_sass.set(settings.get('convert_sass', True))
                self.minify_output.set(settings.get('minify_output', False))
                self.preserve_comments.set(settings.get('preserve_comments', True))
                self.create_backup.set(settings.get('create_backup', True))
                self.extract_inline_styles.set(settings.get('extract_inline_styles', True))
                self.create_project_folder.set(settings.get('create_project_folder', True))
                self.combine_files.set(settings.get('combine_files', True))
                
                last_dir = settings.get('last_output_dir', '')
                if last_dir and os.path.exists(last_dir):
                    self.output_dir.set(last_dir)
        except Exception:
            pass  # Fail silently if can't load settings

    def reset_settings(self):
        """Reset all settings to defaults"""
        self.convert_sass.set(True)
        self.minify_output.set(False)
        self.preserve_comments.set(True)
        self.create_backup.set(True)
        self.extract_inline_styles.set(True)
        self.batch_mode.set(False)
        self.create_project_folder.set(True)
        self.combine_files.set(True)
        
        messagebox.showinfo("Settings Reset", "All settings have been reset to defaults.")
        self.log("⚙ Settings reset to defaults", "info")

    def _on_closing(self):
        """Handle window closing"""
        if self.is_extracting:
            if messagebox.askokcancel("Quit", "Extraction is in progress. Do you want to quit?"):
                self.is_extracting = False
                self.destroy()
        else:
            self._save_settings()
            self.destroy()


class ProjectAnalyzer:
    """Analyze and validate extracted projects"""
    
    @staticmethod
    def analyze_project_structure(project_dir):
        """Analyze the structure of an extracted project"""
        analysis = {
            'has_index': os.path.exists(os.path.join(project_dir, 'index.html')),
            'has_css': os.path.exists(os.path.join(project_dir, 'style.css')),
            'has_js': os.path.exists(os.path.join(project_dir, 'script.js')),
            'has_sass': os.path.exists(os.path.join(project_dir, 'style.scss')),
            'has_backup': any(f.endswith('_original.html') for f in os.listdir(project_dir)),
            'file_count': len([f for f in os.listdir(project_dir) if os.path.isfile(os.path.join(project_dir, f))]),
            'total_size': sum(os.path.getsize(os.path.join(project_dir, f)) 
                            for f in os.listdir(project_dir) 
                            if os.path.isfile(os.path.join(project_dir, f)))
        }
        return analysis
    
    @staticmethod
    def validate_html_references(project_dir):
        """Validate that HTML file correctly references CSS and JS"""
        issues = []
        index_path = os.path.join(project_dir, 'index.html')
        
        if not os.path.exists(index_path):
            issues.append("index.html not found")
            return issues
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Check CSS reference
            if os.path.exists(os.path.join(project_dir, 'style.css')):
                if 'style.css' not in html_content:
                    issues.append("style.css file exists but not referenced in HTML")
            
            # Check JS reference
            if os.path.exists(os.path.join(project_dir, 'script.js')):
                if 'script.js' not in html_content:
                    issues.append("script.js file exists but not referenced in HTML")
                    
        except Exception as e:
            issues.append(f"Error reading index.html: {e}")
        
        return issues


def main():
    """Main application entry point"""
    # Ensure proper GUI scaling on Windows
    if sys.platform == "win32":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    
    # Create and run the application
    app = HTMLExtractorGUI()
    
    # Set application icon if available
    try:
        # You can add an icon file here
        # app.iconbitmap('icon.ico')
        pass
    except Exception:
        pass
    
    # Center window after all widgets are created
    app.center_window()
    
    # Start the main loop
    app.mainloop()


if __name__ == "__main__":
    main()