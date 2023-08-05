from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='yxt_nlp_toolkit',
    version='0.2.0',
    description='common utils for yxt nlp processing',
    long_description=readme(),
    keywords='yunxuetang nlp',
    author='wanglijun',
    author_email='juns1984@qq.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Text Processing :: Linguistic',
    ],
    url='https://github.com/junix/yxt_nlp_toolkit.git',
    packages=[
        'yxt_nlp_toolkit',
        'yxt_nlp_toolkit.common',
        'yxt_nlp_toolkit.utils',
        'yxt_nlp_toolkit.utils.jieba_dict',
        'yxt_nlp_toolkit.embedding',
    ],
    install_requires=[
        # 'gensim==3.4.0',
        'jieba',
    ],
    include_package_data=True,
    zip_safe=False
)
