


from asyncio.windows_events import NULL
import undetected_chromedriver as uc
from selenium.webdriver import Chrome
from selenium import webdriver
import asyncio
from glob import glob
from tqdm import tqdm
from pathlib import Path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import *
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import os
import os.path
import time
import shutil
import random
JS_DROP_FILE = """
    var target = arguments[0],
        offsetX = arguments[1],
        offsetY = arguments[2],
        document = target.ownerDocument || document,
        window = document.defaultView || window;

    var input = document.createElement('INPUT');
    input.type = 'file';
    input.onchange = function () {
      var rect = target.getBoundingClientRect(),
          x = rect.left + (offsetX || (rect.width >> 1)),
          y = rect.top + (offsetY || (rect.height >> 1)),
          dataTransfer = { files: this.files };

      ['dragenter', 'dragover', 'drop'].forEach(function (name) {
        var evt = document.createEvent('MouseEvent');
        evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
        evt.dataTransfer = dataTransfer;
        target.dispatchEvent(evt);
      });

      setTimeout(function () { document.body.removeChild(input); }, 25);
    };
    document.body.appendChild(input);
    return input;
"""
dataset_path  = "d:/automation/dataset"
resultFolder  = "d:/automation/result"
successFolder = "d:/automation/success"
failedFolder = "d:/automation/failed"
download_path = "C:/Users/Hp/Downloads"


def drag_and_drop_file(driver,drop_target, path):
    #driver = drop_target.parent
    file_input = driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(path)

def refresh(driver):
    try:
        
        for x in range(1, 3):
            driver.switch_to.window(driver.window_handles[x])
            driver.close()
    except Exception:
        print("")
    try:
        driver.switch_to.window(driver.window_handles[0])
        driver.delete_all_cookies()
        time.sleep(10)
        driver.get("https://remove.bg/upload")
        WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.CLASS_NAME, 'upload-page')))
    except Exception:
        print("failed reload")
async def main():


    options = uc.ChromeOptions()
    options.add_argument(f'--proxy-server=172.105.184.208:8001')
    driver = uc.Chrome(options,version_main=106)
    
    driver.get("https://remove.bg")
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CLASS_NAME, 'select-photo-file-btn')))
    driver.maximize_window()
    upload = driver.find_elements(By.CLASS_NAME,"select-photo-file-btn")[0]
    driver.execute_script("arguments[0].click();", upload)

    
    WebDriverWait(driver,20).until(EC.url_changes)
    WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.CLASS_NAME, 'upload-page')))
    print("done init")
    im_list = glob(dataset_path+"/*.jpg")+glob(dataset_path+"/*.jpeg")+glob(dataset_path+"/*.png")+glob(dataset_path+"/*.bmp")+glob(dataset_path+"/*.tiff")
    counter_delay_group=0
    for i, im_path in tqdm(enumerate(im_list), total=len(im_list)):
        im_name=im_path.split('/')[-1]
        base_name=im_name.split('\\')[1]
        
        
    
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'upload-page')))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'file-dropzone')))
            dropzone=driver.find_elements(By.CLASS_NAME,"file-dropzone")[0]
            print("UPLOADING "+im_name,end='\t')
            drag_and_drop_file(driver,dropzone,"d:/automation/"+im_name)
            print("[UPLOADED]",end="\t")
            WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-download')))
            time.sleep(random.randrange(1,4,2))
            downloads = driver.find_elements(By.CLASS_NAME, 'btn-download')
            if len(downloads) < 1:
                refresh(driver)
                continue
            
            href= downloads[0].get_attribute("href")
            file_name = href.split('/')[-1]
            downloads[0].click()

            time.sleep(random.randrange(1,4,2))
            WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.CLASS_NAME, 'image-result--delete-btn')))
            close_btn = driver.find_elements(By.CLASS_NAME, 'image-result--delete-btn')
            btns = len(close_btn)
            if btns >= 1:
                for x in range(btns):
                    close_btn[x].click()
            else:
                refresh(driver)
                continue
            time.sleep(random.randrange(1,4,2))
            counter = 0
            while not os.path.exists(download_path+"/"+file_name):
                counter +=1
                if counter >= 30:
                    refresh(driver)
                    break
                    
                time.sleep(1)
            if not os.path.exists(download_path+"/"+file_name):
                continue
            try:
                shutil.move(download_path+"/"+file_name,resultFolder+"/"+base_name)
                if os.path.exists(dataset_path+"/"+base_name):
                    shutil.move(dataset_path+"/"+base_name,successFolder+"/"+base_name)
            except Exception:
                refresh(driver)
            print("[DONE]")
            time.sleep(random.randrange(1,2,1))
            counter_delay_group +=1
            if counter_delay_group == 3:
                time.sleep(random.randrange(10,20,3))
                counter_delay_group=0
            
        except Exception as err:
            try:
                if len(driver.find_elements(By.CLASS_NAME, 'image-result--delete-btn')) >= 1:
                    close_btn = driver.find_elements(By.CLASS_NAME, 'image-result--delete-btn')
                    btns = len(close_btn)
                    #close_btn.click()
                    for x in range(btns):
                        close_btn[x].click()
                    if os.path.exists(dataset_path+"/"+base_name):
                        try:
                            shutil.move(dataset_path+"/"+base_name,failedFolder+"/"+base_name)
                        except Exception :
                            print("err 1")
            except Exception:
                print("err 3")
            refresh(driver)    
                #time.sleep(3600)
    input("Finish...")

if __name__ == '__main__':
    asyncio.run(main())

