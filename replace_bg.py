from PIL import Image
import requests
import base64
import os
import sys

def get_access_token():
    """获取百度API access token"""
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=b5tzPsMmh3Iv0B3qFkAXcgzl&client_secret=AQbiZDu99lIEe1G8nhCnCG8x2Eyhn2V1'
    try:
        response = requests.get(host)
        return response.json()['access_token']
    except Exception as e:
        print(f"获取token失败：{str(e)}")
        return None

def process_image(image_path, rgb_values, access_token):
    """处理单张图片"""
    try:
        with open(image_path, 'rb') as img:
            img_base64 = base64.b64encode(img.read())
        
        request_url = f"https://aip.baidubce.com/rest/2.0/image-classify/v1/body_seg?access_token={access_token}"
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        params = {"image": img_base64, "type": "foreground"}
        
        response = requests.post(request_url, data=params, headers=headers)
        if not response.ok:
            print(f"处理图片 {image_path} 失败")
            return False

        output_path = f"{os.path.splitext(image_path)[0]}.png"
        imgdata = base64.b64decode(response.json()['foreground'])
        
        with open(output_path, 'wb') as f:
            f.write(imgdata)

        # 添加背景色
        im = Image.open(output_path)
        background = Image.new('RGBA', im.size, rgb_values)
        background.paste(im, (0, 0), im)
        background.save(output_path)
        return True
    except Exception as e:
        print(f"处理图片 {image_path} 时发生错误：{str(e)}")
        return False

def main():
    print("请分别输入RGB值，如：222,67,67")
    try:
        rgb = (
            int(input("R: ")),
            int(input("G: ")),
            int(input("B: "))
        )
    except ValueError:
        print("RGB值必须为0-255的整数！")
        return

    access_token = get_access_token()
    if not access_token:
        return

    cur_file = os.path.basename(sys.argv[0])
    image_files = [f for f in os.listdir(".") if f != cur_file and f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for i, image_file in enumerate(image_files, 1):
        print(f"正在处理第 {i} 张图片：{image_file}...")
        if process_image(image_file, rgb, access_token):
            print(f"图片 {image_file} 处理完成！")

if __name__ == "__main__":
    main()