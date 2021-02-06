# plateaupy
![plateaupy](doc/plateaupy.png)

[PLATEAU(CityGML)](https://www.mlit.go.jp/plateau/)のPython版パーサおよびビューア用モジュールです。  
3D表示は[Open3D](http://www.open3d.org/)または[Blender Python (bpy)](https://docs.blender.org/api/current/index.html)で行います。  

## はじめに
本ソフトウェアは、[東京23区から新しい世界を創るアイデアソン／ハッカソン](https://asciistartup.connpass.com/event/198420/)で開発されたものです。  
開発チーム： ***チーム７ （チーム名「影の功労者」，３名）***  
どなたでも使用・開発参加できます。  
本リポジトリにPLATEAU(CityGML)のデータおよび変換したデータは含みません。入手してください。  

機能一覧  
* bldg(建物)のLOD1,LOD2のパース、表示、LOD2テクスチャ表示(遅い)、メタデータのパース
* dem(地表)のパース、表示
* tran(道路)のパース、表示
* Open3D TriangleMesh への変換
* Blender Object への変換
* .plyファイルへの出力

未対応  
* luse(建設予定値)のパース、表示
* brid(橋？)のパース、表示、テクスチャ表示
* codelists定義のパース
* bldg(建物)のLOD3以上のパース、表示

## 動作環境
Python3 (3.6.4で確認)

## インストール
取得
>git clone -recursive https://github.com/AcculusSasao/plateaupy.git  

モジュールインストール

>cd plateaupy  
>pip install -r requirements.txt  

[Open3D v0.11.2](https://github.com/intel-isl/Open3D/releases/tag/v0.11.2) を取得しインストールしてください。  
>pip install open3d-0.11.2-***.whl
  
## PLATEAU(CityGML)データ

### PLATEAU version 0.1の場合 (CityGML_01.zip, CityGML_02.zip)
3ディレクトリを並べて配置します。(違っていても-pathsオプションでパスを指定可能。シンボリックリンクでも良い)  
-- CityGML_01  
&ensp;|- 13100  
-- CityGML_02  
&ensp;|- 13100  
-- plateaupy (このリポジトリ)  
&ensp;|- plateaupy  
&ensp;|- README.md  

### PLATEAU version 0.2の場合 (13100_1.zip ~ 13100_6.zip)
どこかのディレクトリ(例えば"CityGMLver0.2")にデータを展開し、  
以下の appviewer.py 実行時にオプション -paths で指定します。( -paths /path/to/CityGMLver0.2 )  
-- CityGMLver0.2  
&ensp;|- 13100_1  
&ensp;|- 13100_2  
&ensp;|- 13100_3  
&ensp;|- 13100_4  
&ensp;|- 13100_5  
&ensp;|- 13100_6  


## ビューアアプリ appviewer の使い方
1. 区画番号(メッシュコード)一覧を表示します。  
>python appviewer.py -cmd locations  

以下が表示されます。CityGMLへのパスが誤っていると異なります。パスはコマンド引数 -paths で指定することも可能です。  

>locations:  [533925, 533926, 533934, 533935, 533936, 533937, 533944, 533945, 533946, 533947, 533954, 533955, 533956, 533957]  
  
  
2. 区画番号 533925 の、建物(bldg)・道路(tran)・地面(dem) を表示します。-locを指定しなければ全区画を対象としますが時間がかかります。  

>python appviewer.py -loc 533925  

読み込みにしばらく時間がかかります。  
成功するとOpen3Dの3D画面が起動し、マウス操作できます。ESCキーで終了します。  


3. 一度読み込んだデータはキャッシュファイルに保存し、次回以降はコマンドオプション -c を使用することで高速に起動します。  

>python appviewer.py -loc 533925 -c  

4. オプション -k で、gml種類 0:bldg, 1:dem, 2:luse, 3:tran 4:brid を指定できます。  

>python appviewer.py -loc 533925 -c -k 0  

5. オプション -lod2texture でLOD2のテクスチャを表示します。ただし動作が非常に遅いため場所を限定したほうが良いです。  

>python appviewer.py -paths ../CityGML_02 -k 0 -loc 53392633 -lod2texture

6. オプション -plypath [ディレクトリ] で、[ディレクトリ]に .ply ファイルを保存します。
>python appviewer.py -loc 533925 -c -plypath tmp

7. コマンドdumpmetaで、bldg内のメタデータを表示します。  

>python appviewer.py -loc 533925 -c -cmd dumpmeta  

## Blender-Python
![blender](doc/blender.png)
### Blender-Python インストール

[blender/blendertest.sh](blender/blendertest.sh)を参考にしてください。  
Blender 2.91.2 で確認しています。2.8以降bpyの仕様が大きく変わったため、少なくとも2.8以降である必要があります。  
Blender-Python(bpy)はBlender内のPythonで実行されるため、このPythonに必要モジュールをインストールする必要があります。  
Blenderのインストールディレクトリを $BLENDER とすると、まずはpipと必要モジュールをインストールします。  

>BLENDER_PYTHON=$BLENDER/2.91/python/bin/python3.7m  
>$BLENDER_PYTHON -m ensurepip  
>BLENDER_PIP=$BLENDER/2.91/python/bin/pip3  
>$BLENDER_PIP install --upgrade pip  
>$BLENDER_PIP install lxml open3d opencv-python  

### Blender-Python 実行

>$BLENDER/blender --python [blender/blendertest.py](blender/blendertest.py) --python-use-system-env

内容は[blender/blendertest.py](blender/blendertest.py)を参考にしてください。  
args を必要に応じて修正します。  
またBlender表示時にオブジェクト座標をCityGMLのXYZ[meter]そのままだと見づらいため、  
中心位置を vbase という変数に示す値に移動して、表示しています。  

## 課題

既知の不具合・課題 (取消線は解決済)
1. 緯度経度->直交座標変換が、おそらく正確ではない  plutils.py 内 convertPolarToCartsian()
2. 1.と関係するかもしれないが、おそらく、建物・地面・道路の位置が微妙にずれている。
3. ~~建物のポリゴンの法線方向が逆のものがあり、建物の壁が表示されないものがある。~~
4. 道路(tran)の位置情報は高さが全てゼロで、地面(dem)の情報を引っ張ってこなければならない。

あると良さそうなもの
1. 衛星画像をテクスチャとして地面に貼り付ける
2. 動作高速化 (ポリゴン読み込みコードの最適化、ポリゴン数の削減など)
3. [東京公共交通オープンデータ](https://tokyochallenge.odpt.org/)APIの利用

## plateaupyモジュール の説明

>import plateaupy  
>pl = plateaupy.plparser(paths=['../CityGML_01','../CityGML_02'])  

TBD

## ライセンス
[MIT License](LICENSE.txt)  
  
使用している外部モジュールは各々のライセンスに従ってください。  
* earcut-python  
https://github.com/joshuaskelly/earcut-python  
