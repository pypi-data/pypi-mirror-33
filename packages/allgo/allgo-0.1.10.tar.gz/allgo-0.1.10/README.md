# A||GO python library 


## Description
AllGo is a SaaS (Software as a Service) platform provided by Inria. It may be seen as a virtual showroom of technonogies developed by research teams.
First follow https://allgo.inria.fr/users/sign_up to create an account on AllGo (anyone may create such an account). Once your account creation is confirmed, please connect to https://allgo.inria.fr to obtain your private token, which will allow yo to use the AllGo REST API. You will need this token later (cf. §3 below).

## Install 

``` 
  pip install allgo
``` 


## Usage 

###Create a app : 
``` 
  app = allgo.App('ndsafir', token="ead123baaef55412") 
```

NB: token in optional, if you already provide your token with an env variable ALLGO_TOKEN or create a file ~/.allgo_token (without breakline)

###Submit a job : 

```
  files = {'files[0]': open('tmp.png', 'rb')}
  params = '-nopeaks 1 -2dt false -noise 0 -p 1 -bits 8 -iter 5 -adapt 0'
  app.run(files=files, params=params)
```

run is blocking, when finish all files produce by A||Go are download in the current directory 


## Example : 

[https://gitlab.inria.fr/allgo/notebooks/ndsafir](https://gitlab.inria.fr/allgo/notebooks/ndsafir)
  	


	
