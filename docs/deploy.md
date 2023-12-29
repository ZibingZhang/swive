# Delploy to Electric Beanstalk

## Create `requirements.txt`

```shell
# Install dependencies
$ python -m pip install --upgrade pip
$ python -m pip install '.[eb]'
# Create and activate a virtual environment
$ python -m venv eb-venv
$ source eb-venv/bin/activate
# Install and freeze dependencies
$ python -m pip install --upgrade pip
$ python -m pip install .
$ python -m  pip freeze > requirements.txt
$ sed -i '' '/swive/d' requirements.txt
$ deactivate
```

## Deploy site with the EB CLI

```shell
$ source venv/bin/activate
# Initialize the EB CLI repository
$ eb init -ip python-3.11 swive
```

If no environment exists, create an environment.

```shell
# Create an environment and deploy the app to it
$ eb create swive-env --single
```

Otherwise, use an existing environment.

```shell
# Set the default environment
$ eb use swive-env
```

```shell
# Find the domain name of the environment
$ eb status
Environment details for: swive-env
  Application name: swive
  ...
  CNAME: swive-env.XXX.us-east-2.elasticbeanstalk.com
  ...
```

Add the domain name to the [`ALLOWED_HOSTS`](../swive/settings/production.py) setting.

```python
ALLOWED_HOSTS = [
    ...,
    "swive-env.XXX.us-east-2.elasticbeanstalk.com",
]
```

```shell
# Define environment variables
$ eb setenv SECRET_KEY='XXX'
$ eb setenv DJANGO_SUPERUSER_USERNAME='XXX'
$ eb setenv DJANGO_SUPERUSER_PASSWORD='XXX'
$ eb setenv DJANGO_SUPERUSER_EMAIL='XXX'
# Confirm environment variables are set
$ eb printenv
```

Save the file, then deploy.

```shell
$ git add -A
$ eb deploy --staged
$ eb open
```

## Confirm Environment Configurations

### WSGI Path

`swive.wsgi:application`

### Static Files

| Path    | Directory | 
|---------|-----------|
| /static | static    |

### Environment Properties

| Name                      | Value                              | 
|---------------------------|------------------------------------|
| DJANGO_SUPERUSER_EMAIL    | XXX                                |
| DJANGO_SUPERUSER_PASSWORD | XXX                                |
| DJANGO_SUPERUSER_USERNAME | XXX                                |
| PYTHONPATH                | /var/app/venv/staging-LQM1lest/bin |
| SECRET_KEY                | XXX                                |

## Set Up a Custom Domain with HTTPS

Create a CNAME record pointing at the environment's domain name.

| Host Name | Type  | TTL  | Data                                          |
|-----------|-------|------|-----------------------------------------------|
| XXX       | CNAME | 3600 | swive-env.XXX.us-east-2.elasticbeanstalk.com. |

Request a certificate with [AWS Certificate Manager](https://us-east-2.console.aws.amazon.com/acm/home).
Validate the certificate by creating a CNAME record as instructed.

Under "Instance traffic and scaling", add a listener with the following settings:

- port: 443
- protocol: HTTPS
- SSL certificate: \<certificate\>
- SSL policy: ELBSecurityPolicy-TLS13-1-2-2021-06

## Using EC2 Instance Connect

Each EB environment is backed by an EC2 instance.
Navigate to EC2 and connect with EC2 Instance Connect.

| Path                            | Description         |
|---------------------------------|---------------------|
| `/var/app/current`              | Current deployment  |
| `/var/app/venv/staging-LQM1lest | Virtual environment |

## Resources

### Amazon Web Services 

- [Deploying a Django application to Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html)
- [DNS validation](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html)
- [Configuring HTTPS for your Elastic Beanstalk environment](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https.html)
- [Configuring your Elastic Beanstalk environment's load balancer to terminate HTTPS](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/configuring-https-elb.html)
- [TLS listeners for your Network Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-tls-listener.html)

## Stack Overflow

- [Fixing SSL: CERTIFICATE_VERIFY_FAILED](https://stackoverflow.com/a/53310545)