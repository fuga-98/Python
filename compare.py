import sys
import os
import glob
import hashlib
import shutil
import difflib
def main():
    # 引数の一つ目はスクリプト名
    if len(sys.argv) != 3:
        print("引数の数が二つではありません")
        return
    _,folder1,folder2 =sys.argv
    # フォルダ構成を確認
    if not compare_folder(folder1,folder2):
        print("フォルダ構成が違います")
        return
    # ソートしたファイル格納用
    if not os.path.exists('sorted'):
        os.makedirs('sorted')
    # ソートファイルを作成
    compare_and_sort_files(folder1,folder2,True) 
    sorted_path1 = os.path.join('sorted',folder1)
    sorted_path2 = os.path.join('sorted',folder2)
    # ソートファイルのハッシュ値確認
    matcher,differ=compare_and_sort_files(sorted_path1,sorted_path2,False)
    print(f"一致ファイル：{matcher}")
    print(f"差分ありファイル:{differ}")
    # htmlで差分を出力
    make_diff_files(sorted_path1,sorted_path2)

    
# フォルダの内部を比較
# 引数：実行する直下にあるフォルダ１、フォルダ２
# 戻り値：bool
def compare_folder(folder1,folder2):
    # パスの設定 
    files1=_get_files_list(folder1)
    files2=_get_files_list(folder2)
    files_set1=_get_filenames_set(files1)
    files_set2=_get_filenames_set(files2)
    if files_set1==files_set2:
        return True
    diff = files_set1^files_set2
    
    return False
#compare_folder("a","b")


# フォルダの中のファイルを比較
# 引数：実行する直下にあるフォルダ１、フォルダ２,新しくファイルを作るかどうかフラグ
# sortedフォルダにハッシュ値が異なるファイルの場合は中身をソートし、新しいファイルを作成する。一緒の場合はそのままsortedに。
# 戻り値：一致したリスト、一致しないリスト
def compare_and_sort_files(folder1,folder2,make_file_flag=True):
    match_files=list()
    diff_files=list()
    files1=sorted(_get_files_list(folder1))
    files2=sorted(_get_files_list(folder2))
    # 一応チェック
    if not _check_filenames_macth(files1,files2):
        return 
    for index,file in enumerate(files1):
        #ハッシュ値が等しい場合はコピー、異なる場合はソート
        if _check_hash_match(file,files2[index]):
            match_files.append(file)
            if make_file_flag:
                _copy_file(file)
                _copy_file(files2[index])
        else:
            diff_files.append(file)
            if make_file_flag:
                make_sorted_contents(file)
                make_sorted_contents(files2[index])
    return match_files,diff_files
 # compare_and_sort_files("a","b")  
# ファイルの差分をHTML方式で出力する。
# 引数：フォルダ　ファイル中はソートされていることを期待
# 戻り値：なし、ファイルを作成
def make_diff_files(folder1,folder2):
    file_count=0
    files_path1=sorted(_get_files_list(folder1))
    files_path2=sorted(_get_files_list(folder2))
    if not _check_filenames_macth(files_path1,files_path2):
        return False
    for index,path1 in enumerate(files_path1):
        _make_diff_html(path1,files_path2[index])
        file_count+=1
    print(f'作成ファイル数：{file_count}')


def _get_files_list(folder):
    path = os.path.join(".", folder,"*")
    files=glob.glob(path)
    return files


def _get_filenames_set(file_list):
    file_set =set()
    for file in file_list:
        file_name=os.path.basename(file)
        file_set.add(file_name)  
    return file_set

def _check_filenames_macth(files1,files2):
    if _get_filenames_set(files1) != _get_filenames_set(files2):
            print(f"ファイル名空間に差分があるよ {_get_filenames_set(files1)^_get_filenames_set(files2)}")
            return False
    return True

# 指定されたファイルのSHA-256ハッシュ値を計算して返す関数
def _calc_sha256_files(file_path):
    sha256 =hashlib.sha256()
  # バイナリモードでファイルを開く
    with open(file_path,'rb')  as f:
      for chunk in iter(lambda: f.read(4096),b''):
          sha256.update(chunk)
    return sha256.hexdigest()
#_calc_sha256_files(".\\a\\apple.txt")

# ２つのファイルのハッシュ値が等しいか計算
def _check_hash_match(file_path1,file_path2):
    if _calc_sha256_files(file_path1) == _calc_sha256_files(file_path2):
        return True
    return False

# ファイルの中身をソートして新しいファイルを作成する。引数のパスは文字列
def make_sorted_contents(file_path):
    with open(file_path, 'r') as f:
        contents = f.readlines()
        # ファイルの最後の行に改行がない場合、改行を追加
        if contents and not contents[-1].endswith('\n'):
            contents[-1] += '\n'
        sorted_contents = sorted(contents)
    # ファイルのディレクトリを確認し、存在しない場合は作成する
    new_file_path = os.path.join(".", "sorted", file_path[2:])
    directory = os.path.dirname(new_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(new_file_path, 'w') as f:
        f.writelines(sorted_contents)


# path = '.\\a\\apple.txt'
# make_sorted_contents(path)

# ファイルをこぴーしてsortedフォルダに格納
def _copy_file(file_path):
    new_file_path = os.path.join(".", "sorted", file_path[2:])
    directory = os.path.dirname(new_file_path)
    # if not os.path.exists(directory):
    #     os.makedirs(directory)
    shutil.copy2(file_path, directory)


# path2='.\\a\\bean.txt'
# _copy_file(path2)
    
# 差分のhtmlファイルを作成する。引数はファイルのパス
def _make_diff_html(file_path1,file_path2):
    with open(file_path1,'r') as f1, open(file_path2,'r') as f2:
        content1 = f1.readlines()
        content2 = f2.readlines()
    differ= difflib.HtmlDiff()
    html_diff = differ.make_file(content1,content2)
    file_name, _ = os.path.splitext(os.path.basename(file_path1)) 
    file_name_with_ext = file_name +'.html'
    file_path_to_make = os.path.join(".","diff", file_name_with_ext)
    if not os.path.exists("diff"):
        os.makedirs("diff")
    with open(file_path_to_make,'w') as f:
        f.write(html_diff)

if __name__ == "__main__":
    main()

    
        
    

        



    

