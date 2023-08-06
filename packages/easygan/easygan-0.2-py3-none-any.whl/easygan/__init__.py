from PIL import Image
import requests
from bs4 import BeautifulSoup
import subprocess
import os
import sys
import glob
import argparse


IMG_DIR = "results"

def download_file(url, local_filename=None):
    if local_filename is None:
        local_filename = url.split('/')[-1]
    #local_filename = url.split('/')[-1]
    if os.path.exists(local_filename):
        return local_filename
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename

def get_images(search, keyword, folder):
    imgCounter = 0  # for image name
    #print('start collecting images')
    
    # create a folder
    target_dir = os.getcwd() + "/"
    #folderName = input("Type a folder name for images: ")
    #os.system('mkdir -p ' + target_dir + folderName)
    os.system('mkdir -p ' + target_dir + folder)


    # ToDo there is a limitation which can't images more than 800
    number = 2000

    maxCounter = number/20
    tmp = int(number/20)
    if tmp > 0:
        maxCounter = tmp + 1
    # queryString = input("enter the word: ")
    # queryString = queryString.replace(' ', '+')

    queryString = keyword
    
    # space --> +
    for cnt in range(0, maxCounter):
        start = cnt*20
        print('start :' + str(start))
        url = 'https://www.google.com/search?q={0}&gbv=1&ie=UTF-8&tbm=isch&prmd=ivnsba&ei=K9Z4Wo_qIMjW5gKJq5vQCw&start={1}&sa=N'.format(
            queryString, start)
        print(url)
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')
        images = soup.select('img')

        for i, image in enumerate(images):
            img_url = image.get('src')
            savedname = target_dir + folder + '/' + 'img%04d.png' % imgCounter
            imgCounter += 1
            try:
                filename = download_file(img_url, savedname)
            except Exception as e:
                print(e)
                continue


# DCGAN
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Reshape
from keras.layers.core import Activation
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import UpSampling2D
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.core import Flatten
from keras.optimizers import Adam
import numpy as np
import random

n_colors = 3

def generator_model():
    model = Sequential()

    model.add(Dense(1024, input_shape=(100,)))
    model.add(Activation('tanh'))

    model.add(Dense(128*16*16))
    model.add(BatchNormalization())
    model.add(Activation('tanh'))

    model.add(Reshape((16, 16, 128)))
    model.add(UpSampling2D(size=(2,2)))
    model.add(Conv2D(64, (5,5), padding='same'))
    model.add(Activation('tanh'))

    model.add(UpSampling2D(size=(2,2)))
    model.add(Conv2D(n_colors, (5,5), padding='same'))
    model.add(Activation('tanh'))

    return model

def discriminator_model():
    model = Sequential()

    model.add(Conv2D(64, (5, 5), input_shape=(64, 64, n_colors), padding='same'))
    model.add(Activation('tanh'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(128, (5,5)))
    model.add(Activation('tanh'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Flatten())

    model.add(Dense(1024))
    model.add(Activation('tanh'))

    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    return model


def generator_containing_discriminator(generator, discriminator):
    model = Sequential()
    model.add(generator)
    model.add(discriminator)
    return model

def image_batch(filePath, batchSize):
    #print("file path: " + filePath)
    #print("batch size: " + str(batchSize))
    source_dir = os.getcwd() + "/"
    files = glob.glob(source_dir + filePath + "/*.png", recursive=True)
    files = random.sample(files, int(batchSize))
    res = []
    for path in files:
        image = Image.open(path)
        image = image.resize((64, 64))
        arr = np.array(image)
        arr = (arr-127.5)/127.5
        arr.resize((64, 64, n_colors))
        res.append(arr)
    return np.array(res)

def combineImages(generated_images, cols=5, rows=5):
    shape = generated_images.shape
    h = shape[1]
    w = shape[2]

    image = np.zeros((rows * h, cols * w, n_colors))
    for index, img in enumerate(generated_images):
        if index >= cols * rows:
            break
        i = index // cols
        j = index % cols

        image[i*h:(i+1)*h, j*w:(j+1)*w, :] = img[:, :, :]
        image = image * 127.5 + 127.5
        image = Image.fromarray(image.astype(np.uint8))
        return image

def train(model, trainable):
    model.trainable = trainable
    for layer in model.layers:
        layer.trainable = trainable


def run_DCGAN(filePath, batchSize):
    # batch_size = int(batchSize)
    #print("file path :" + filePath)
    batch_size = int(batchSize)
    discriminator = discriminator_model()
    generator = generator_model()

    discriminator_on_generator = generator_containing_discriminator(generator, discriminator)
    train(discriminator, False)
    discriminator_on_generator.compile(loss='binary_crossentropy', optimizer=Adam(lr=0.0002, beta_1=0.5))
    print(generator.summary())
    print(discriminator.summary())

    train(discriminator, True)
    discriminator.compile(loss='binary_crossentropy', optimizer=Adam(lr=0.0002, beta_1=0.5))
    print(discriminator.summary())

    for i in range(30 * 1000):
        batch_image = image_batch(filePath, batch_size)
        noise = np.random.uniform(size=[batch_size, 100], low=-1.0, high=1.0)
        generated_images = generator.predict(noise)
        X = np.concatenate((batch_image, generated_images))
        y = [1] * batch_size + [0] * batch_size
        d_loss = discriminator.train_on_batch(X, y)
        noise = np.random.uniform(size=[batch_size, 100], low=-1.0, high=1.0)
        g_loss = discriminator_on_generator.train_on_batch(noise, [1]*batch_size)

        if i % 100 == 0:
            print("step %d d_loss, g_loss: %g %g" %(i, d_loss, g_loss))
            image = combineImages(generated_images)
            # ToDo get file path info
            #os.system('mkdir -p ./' + IMG_DIR)
            target_dir = os.getcwd() + "/"
            os.system('mkdir -p ' + target_dir + IMG_DIR)
            image.save(target_dir + IMG_DIR + "/gen%05d.png" % i)



def randomName():
    letters = "abcdefghijklmnopqrstuvwxyz"
    folderName = ""
    for i in range(0,5):
        folderName = folderName + choice(letters)
    return folderName

def main():
    # args
    parser = argparse.ArgumentParser(description="easygan")
    parser.add_argument("-s", "--search", dest="search", help="search engine google or flickr")
    parser.add_argument("-k", "--keyword", dest="keyword", help="search keyword")
    parser.add_argument("-f", "--folder", dest="folder", help="folder name")
    parser.add_argument("-b", "--batch", dest="batch", help="default batch_size: 55")
    
    args = parser.parse_args()


    search = args.search
    keyword = args.keyword
    folder = args.folder
    batch = args.batch

    if search is not None and keyword is not None:
        if folder is None:
            folder = randomName()
        print("start collecting images")
        # collect images from google  
        # ToDo flickr
        # requirements API Key and Secret Key
        get_images(search, keyword, folder)
        print("finish collecting images")

    if batch is not None:
        print("start DCGAN")
        # if batch is None:
        #     batch = 55
        run_DCGAN(folder, batch)
        print("finish generating images")
    


if __name__ == '__main__':
    main()
