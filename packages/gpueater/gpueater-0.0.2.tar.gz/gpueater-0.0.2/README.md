# GPUEater Console API

## Getting Started
GPUEater is a cloud computing service focusing on Machine Learning and Deep Learning. Now, AMD Radeon GPUs and NVIDIA Quadro GPUs are available. 

This document is intended to describe how to set up this API and how to control your instances through this API.

Before getting started, register your account on GPUEater.
https://www.gpueater.com/

### Prerequisites
1. Python 3.x is required to run GPUEater API console.
2. Create a JSON file in accordance with the following instruction.

At first, open your account page(https://www.gpueater.com/console/account) and copy your access_token. The next, create a JSON file on ~/.eater

```
{
        "gpueater": {
                "access_token":"[YourAccessToken]",
                "secret_token":"[YourSecretToken]"
        }
}
```

or

```
{
        "gpueater": {
                "email":"[YourEmail]",
                "password":"[YourPassword]"
        }
}
```
* At this time, permission control for each token is not available. Still in development.

## Installation

Add this line to your application's Gemfile:

```python
pip3 install gpueater
```

## Run GPUEater API

Before launching an instance, you need to decide product, ssh key, OS image. Get each info with the following APIs.

#### Get available on-demand product list

This API returns current available on-demand products.
```
import gpueater

res = gpueater.ondemand_list()
print(res)
```
#### Get registered ssh key list

This API returns your registered ssh keys.
```
import gpueater

res = gpueater.ssh_keys()
print(res)
```

#### Get OS image list

This API returns available OS images.
```
import gpueater

res = gpueater.image_list()
print(res)
```

#### Instance launch

Specify product, OS image, and ssh_key for instance launching. 

```
import gpueater

res = gpueater.ondemand_list()

image = res.find_image('Ubuntu16.04 x64')
ssh_key = res.find_ssh_key('[Your ssh key]')
product = res.find_product('a1.rx580')

param = {
    'product_id' : product['id'],
    'image' : image['alias'],
    'ssh_key_id' : ssh_key['id'],
    'tag' : 'HappyGPUProgramming'
}

res = gpueater.launch_ondemand_instance(param)
puts res
```
In the event, the request has succeeded, then the API returns the following empty data.
{data:null, error:null} 

In the event, errors occurred during the instance instantiation process, then the API returns details about the error.

#### Launched instance list

This API returns your launched instance info.
```
import gpueater

res = gpueater.instance_list()
```
#### Terminate instance

Before terminating an instance, get instance info through instance list API. Your instance_id and machine_resource_id are needed to terminate.

```
import gpueater

res = gpueater.instance_list()
for ins in res:
	if ins['tag'] == 'HappyGPUProgramming':
		print(gpueater.terminate_instance(e))
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
