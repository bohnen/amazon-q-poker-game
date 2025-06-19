"""
クリップボード操作のユーティリティ
"""

import subprocess
import sys
from typing import Optional

class ClipboardManager:
    """クリップボード管理クラス"""
    
    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """テキストをクリップボードにコピー"""
        try:
            if sys.platform == "darwin":  # macOS
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                process.communicate(text.encode('utf-8'))
                return process.returncode == 0
            
            elif sys.platform == "win32":  # Windows
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                process.communicate(text.encode('utf-8'))
                return process.returncode == 0
            
            elif sys.platform.startswith("linux"):  # Linux
                # xclipを試す
                try:
                    process = subprocess.Popen(['xclip', '-selection', 'clipboard'], 
                                             stdin=subprocess.PIPE)
                    process.communicate(text.encode('utf-8'))
                    return process.returncode == 0
                except FileNotFoundError:
                    # xselを試す
                    try:
                        process = subprocess.Popen(['xsel', '--clipboard', '--input'], 
                                                 stdin=subprocess.PIPE)
                        process.communicate(text.encode('utf-8'))
                        return process.returncode == 0
                    except FileNotFoundError:
                        return False
            
            return False
            
        except Exception as e:
            print(f"クリップボードコピーエラー: {e}")
            return False
    
    @staticmethod
    def get_from_clipboard() -> Optional[str]:
        """クリップボードからテキストを取得"""
        try:
            if sys.platform == "darwin":  # macOS
                result = subprocess.run(['pbpaste'], capture_output=True, text=True)
                return result.stdout if result.returncode == 0 else None
            
            elif sys.platform == "win32":  # Windows
                # PowerShellを使用
                result = subprocess.run(['powershell', '-command', 'Get-Clipboard'], 
                                      capture_output=True, text=True)
                return result.stdout.strip() if result.returncode == 0 else None
            
            elif sys.platform.startswith("linux"):  # Linux
                # xclipを試す
                try:
                    result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                                          capture_output=True, text=True)
                    return result.stdout if result.returncode == 0 else None
                except FileNotFoundError:
                    # xselを試す
                    try:
                        result = subprocess.run(['xsel', '--clipboard', '--output'], 
                                              capture_output=True, text=True)
                        return result.stdout if result.returncode == 0 else None
                    except FileNotFoundError:
                        return None
            
            return None
            
        except Exception as e:
            print(f"クリップボード取得エラー: {e}")
            return None
