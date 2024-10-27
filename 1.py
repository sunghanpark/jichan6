import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from ttkbootstrap import Style
import PyPDF2
import os

class LineNumberedText(scrolledtext.ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_numbers = tk.Canvas(
            self.master,
            width=30,
            bg='#f0f0f0',
            highlightthickness=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.bind('<KeyPress>', self._on_key_press)
        self.bind('<KeyRelease>', self._on_key_release)
        self.bind('<MouseWheel>', self._on_mouse_wheel)
        self.bind('<Configure>', self._on_configure)
        self.bind('<<Modified>>', self._on_modified)
        self.after(10, self._update_line_numbers)
    
    def _on_key_press(self, event):
        self.after(10, self._update_line_numbers)
    
    def _on_key_release(self, event):
        self.after(10, self._update_line_numbers)
    
    def _on_mouse_wheel(self, event):
        self.after(10, self._update_line_numbers)
    
    def _on_configure(self, event):
        self.after(10, self._update_line_numbers)
    
    def _on_modified(self, event):
        self.after(10, self._update_line_numbers)
    
    def _update_line_numbers(self):
        self.line_numbers.delete('all')
        i = self.index('@0,0')
        while True:
            dline = self.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split('.')[0]
            self.line_numbers.create_text(
                15, y, text=linenum,
                anchor='center',
                font=('Consolas', 10),
                fill='#606060'
            )
            i = self.index(f'{i}+1line')

class TextDiffGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("텍스트 & PDF 비교 프로그램")
        self.root.geometry("1200x800")
        
        style = Style(theme='cosmo')
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 입력 프레임
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽 텍스트 영역
        left_frame = ttk.LabelFrame(input_frame, text="첫 번째 텍스트/PDF", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        left_upload_frame = ttk.Frame(left_frame)
        left_upload_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.left_file_label = ttk.Label(left_upload_frame, text="선택된 파일 없음")
        self.left_file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        left_upload_btn = ttk.Button(
            left_upload_frame,
            text="파일 업로드",
            command=lambda: self.upload_pdf(1),
            style='info.TButton'
        )
        left_upload_btn.pack(side=tk.RIGHT, padx=5)
        
        self.text1 = LineNumberedText(
            left_frame,
            wrap=tk.NONE,
            width=40,
            height=15,
            font=('Consolas', 12),
            undo=True
        )
        self.text1.pack(fill=tk.BOTH, expand=True)
        
        # 오른쪽 텍스트 영역
        right_frame = ttk.LabelFrame(input_frame, text="두 번째 텍스트/PDF", padding="10")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_upload_frame = ttk.Frame(right_frame)
        right_upload_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.right_file_label = ttk.Label(right_upload_frame, text="선택된 파일 없음")
        self.right_file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        right_upload_btn = ttk.Button(
            right_upload_frame,
            text="파일 업로드",
            command=lambda: self.upload_pdf(2),
            style='info.TButton'
        )
        right_upload_btn.pack(side=tk.RIGHT, padx=5)
        
        self.text2 = LineNumberedText(
            right_frame,
            wrap=tk.NONE,
            width=40,
            height=15,
            font=('Consolas', 12),
            undo=True
        )
        self.text2.pack(fill=tk.BOTH, expand=True)
        
        # 옵션 프레임
        options_frame = ttk.LabelFrame(main_frame, text="비교 옵션", padding="10")
        options_frame.pack(fill=tk.X, pady=10)
        
        self.compare_mode = tk.StringVar(value="detail")
        ttk.Radiobutton(options_frame, text="상세 비교", value="detail", 
                       variable=self.compare_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(options_frame, text="단어 단위 비교", value="word", 
                       variable=self.compare_mode).pack(side=tk.LEFT, padx=10)
        
        self.case_sensitive = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="대소문자 구분", 
                       variable=self.case_sensitive).pack(side=tk.LEFT, padx=10)
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.X)
        
        compare_button = ttk.Button(
            button_frame,
            text="텍스트 비교",
            command=self.compare_texts,
            style='primary.TButton',
            padding=10
        )
        compare_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(
            button_frame,
            text="초기화",
            command=self.clear_texts,
            style='secondary.TButton',
            padding=10
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # 결과 프레임
        result_frame = ttk.LabelFrame(main_frame, text="비교 결과", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = LineNumberedText(
            result_frame,
            wrap=tk.NONE,
            width=80,
            height=15,
            font=('Consolas', 12)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 상태바
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            padding=5
        )
        status_bar.pack(fill=tk.X)
        
        # 태그 설정
        self.text1.tag_configure("diff", background="yellow", foreground="red")
        self.text2.tag_configure("diff", background="yellow", foreground="red")
        self.result_text.tag_configure("diff", background="yellow", foreground="red")
        
        # 스크롤바 설정
        self._setup_scrollbars()
    def _setup_scrollbars(self):
        x_scroll1 = ttk.Scrollbar(self.text1.master, orient=tk.HORIZONTAL, command=self.text1.xview)
        x_scroll1.pack(side=tk.BOTTOM, fill=tk.X)
        self.text1.configure(xscrollcommand=x_scroll1.set)
        
        x_scroll2 = ttk.Scrollbar(self.text2.master, orient=tk.HORIZONTAL, command=self.text2.xview)
        x_scroll2.pack(side=tk.BOTTOM, fill=tk.X)
        self.text2.configure(xscrollcommand=x_scroll2.set)
        
        x_scroll_result = ttk.Scrollbar(self.result_text.master, orient=tk.HORIZONTAL, command=self.result_text.xview)
        x_scroll_result.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_text.configure(xscrollcommand=x_scroll_result.set)

    def extract_text_from_pdf(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            messagebox.showerror("오류", f"PDF 파일 읽기 오류: {str(e)}")
            return None

    def upload_pdf(self, text_box_num):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF 파일", "*.pdf"), ("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        
        if not file_path:
            return
            
        file_name = os.path.basename(file_path)
        
        if file_path.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            except Exception as e:
                messagebox.showerror("오류", f"파일 읽기 오류: {str(e)}")
                return
        
        if text is not None:
            if text_box_num == 1:
                self.text1.delete("1.0", tk.END)
                self.text1.insert(tk.END, text)
                self.left_file_label.config(text=file_name)
            else:
                self.text2.delete("1.0", tk.END)
                self.text2.insert(tk.END, text)
                self.right_file_label.config(text=file_name)
            
            self.status_var.set(f"✅ 파일 '{file_name}' 업로드 완료")
    
    def compare_texts(self):
        text1 = self.text1.get("1.0", tk.END).strip()
        text2 = self.text2.get("1.0", tk.END).strip()
        
        if not text1 or not text2:
            self.status_var.set("⚠️ 두 텍스트를 모두 입력해주세요.")
            return
        
        if not self.case_sensitive.get():
            text1 = text1.lower()
            text2 = text2.lower()
        
        self.result_text.delete("1.0", tk.END)
        
        if self.compare_mode.get() == "word":
            self.compare_words(text1, text2)
        else:
            result, diff_count = self.analyze_code_differences(text1, text2)
            self.show_detailed_result(result, diff_count)
    
    def analyze_code_differences(self, text1, text2):
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        result = []
        diff_count = 0
        
        max_len = max(len(lines1), len(lines2))
        lines1.extend([''] * (max_len - len(lines1)))
        lines2.extend([''] * (max_len - len(lines2)))
        
        for i, (line1, line2) in enumerate(zip(lines1, lines2)):
            if line1 != line2:
                diff_count += 1
                result.append(f"\n{i+1}  차이점 #{diff_count}:\n")
                result.append("-" * 50 + "\n")
                
                result.append(f"▶ 줄 내용:\n")
                result.append(f"{i+1}  텍스트1: '{line1}'\n")
                result.append(f"{i+1}  텍스트2: '{line2}'\n\n")
                
                space_diff1 = len(line1) - len(line1.lstrip())
                space_diff2 = len(line2) - len(line2.lstrip())
                if space_diff1 != space_diff2:
                    result.append(f"▶ 들여쓰기 차이:\n")
                    result.append(f"  텍스트1: {space_diff1}칸\n")
                    result.append(f"  텍스트2: {space_diff2}칸\n\n")
                
                special_chars1 = [char for char in line1 if not char.isalnum() and not char.isspace()]
                special_chars2 = [char for char in line2 if not char.isalnum() and not char.isspace()]
                if special_chars1 != special_chars2:
                    result.append(f"▶ 특수문자 차이:\n")
                    result.append(f"  텍스트1: {special_chars1 if special_chars1 else '[없음]'}\n")
                    result.append(f"  텍스트2: {special_chars2 if special_chars2 else '[없음]'}\n")
                
                result.append("-" * 50 + "\n")
        
        return result, diff_count
    
    def compare_words(self, text1, text2):
        words1 = text1.split()
        words2 = text2.split()
        
        max_len = max(len(words1), len(words2))
        words1.extend([''] * (max_len - len(words1)))
        words2.extend([''] * (max_len - len(words2)))
        
        result = []
        diff_count = 0
        
        for i, (word1, word2) in enumerate(zip(words1, words2)):
            if word1 != word2:
                result.append(f"단어 {i+1}:\n")
                result.append(f"텍스트1: '{word1}'\n")
                result.append(f"텍스트2: '{word2}'\n")
                result.append("-" * 30 + "\n")
                diff_count += 1
        
        self.show_comparison_result(result, diff_count)
        self.highlight_word_differences(words1, words2)
    
    def show_detailed_result(self, result, diff_count):
        if diff_count > 0:
            summary = f"분석 완료: 총 {diff_count}개의 차이점이 발견되었습니다.\n\n"
            self.result_text.insert(tk.END, summary)
            self.result_text.insert(tk.END, "".join(result))
            
            self.apply_result_styles()
            
            self.status_var.set(f"✅ 분석 완료: {diff_count}개의 차이점 발견")
        else:
            self.result_text.insert(tk.END, "두 텍스트가 완전히 동일합니다.")
            self.status_var.set("✅ 분석 완료: 차이점이 없습니다")
        
        self.highlight_differences(self.text1.get("1.0", tk.END), self.text2.get("1.0", tk.END))
    
    def show_comparison_result(self, result, diff_count):
        if diff_count > 0:
            header = f"총 {diff_count}개의 차이점이 발견되었습니다.\n\n"
            self.result_text.insert(tk.END, header)
            self.result_text.insert(tk.END, "".join(result))
            self.status_var.set(f"✅ 비교 완료: {diff_count}개의 차이점 발견")
        else:
            self.result_text.insert(tk.END, "두 텍스트가 완전히 동일합니다.")
            self.status_var.set("✅ 비교 완료: 차이점이 없습니다")
    
    def highlight_differences(self, text1, text2):
        self.clear_highlights()
        
        lines1 = text1.splitlines()
        lines2 = text2.splitlines()
        
        for i, (line1, line2) in enumerate(zip(lines1, lines2)):
            if line1 != line2:
                start_pos1 = f"{i+1}.0"
                start_pos2 = f"{i+1}.0"
                
                end_pos1 = f"{i+1}.{len(line1)}"
                end_pos2 = f"{i+1}.{len(line2)}"
                
                self.text1.tag_add("diff", start_pos1, end_pos1)
                self.text2.tag_add("diff", start_pos2, end_pos2)
    
    def highlight_word_differences(self, words1, words2):
        self.clear_highlights()
        
        text1 = self.text1.get("1.0", tk.END)
        text2 = self.text2.get("1.0", tk.END)
        
        for word in set(words1 + words2):
            if word and (word in words1) != (word in words2):
                self.highlight_word(self.text1, word)
                self.highlight_word(self.text2, word)
    
    def highlight_word(self, text_widget, word):
        start = "1.0"
        while True:
            start = text_widget.search(word, start, tk.END)
            if not start:
                break
            end = f"{start}+{len(word)}c"
            text_widget.tag_add("diff", start, end)
            start = end
    
    def clear_highlights(self):
        self.text1.tag_remove("diff", "1.0", tk.END)
        self.text2.tag_remove("diff", "1.0", tk.END)
    
    def apply_result_styles(self):
        self.result_text.tag_configure("heading", font=('Consolas', 12, 'bold'))
        self.result_text.tag_configure("diff_count", foreground="blue")
        self.result_text.tag_configure("separator", foreground="gray")
        
        start = "1.0"
        
        while True:
            start = self.result_text.search("차이점 #", start, tk.END)
            if not start:
                break
            line_end = self.result_text.search("\n", start)
            self.result_text.tag_add("heading", start, line_end)
            start = line_end
        
        start = "1.0"
        while True:
            start = self.result_text.search("-" * 50, start, tk.END)
            if not start:
                break
            line_end = self.result_text.search("\n", start)
            self.result_text.tag_add("separator", start, line_end)
            start = line_end
    
    def clear_texts(self):
        self.text1.delete("1.0", tk.END)
        self.text2.delete("1.0", tk.END)
        self.result_text.delete("1.0", tk.END)
        self.status_var.set("")
        self.left_file_label.config(text="선택된 파일 없음")
        self.right_file_label.config(text="선택된 파일 없음")
        self.clear_highlights()

if __name__ == "__main__":
    root = tk.Tk()
    app = TextDiffGUI(root)
    root.mainloop()