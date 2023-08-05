from distutils.core import setup

setup(
    name='funcoperators',
    version='0.2',
    description='Allow infix function notation like (1,2) /dot/ (3,4) for dot((1,2), (3,4) or 1 /frac/ 3 for frac(1,3).',
    author='Robert Vanden Eynde',
    author_email='robertvandeneynde@hotmail.com',
    packages=['funcoperators'], # 'mymath.adv'
    url='https://github.com/robertvandeneynde/python',
)
