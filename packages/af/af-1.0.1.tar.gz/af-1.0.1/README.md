# Af2bilingual

## Install in ubuntu 16.04

### 1. First install libicu

```
sudo apt-get update
sudo apt-get install libicu-dev
```

### 2. Install Af
To install it globally:
```
pip install Af
```

In a virtual environment:
```
virtualenv -p python3 venv
source venv/bin/activate 
pip install Af
```

## Usage
Let's suppose you have a directory "my_dir" with af files. To generate bilinguals file:
```
af2bilingual my_dir
```

All generated files will be located in a generated "bilingual" directory next to "my_dir"
If the bilingual directory already exists the ad2bilingual will fail except if you use :
```
af2bilingual my_dir -o
if you want 
```


