# Python client for voximplant.com HTTP API

This is a simple client for [voximplant.com](https://voximplant.com) HTTP API. It is intended as an ad-hoc scenario runner and uploader, but may easily be used for any API manipulations.

## Installation

```sh
$ pip install voximplant_client
```

## CLI Usage

```sh
# `VOXIMPLANT_ACCOUNT_ID` and `VOXIMPLANT_API_KEY` environment variables are used
$ voximplant upload ./test.js  # upload the scenario

# explicit account id and api key
voximplant --account-id=100500 --api-key=<YOUR-key> upload ./test.js
```

### Running a scenario
This client has a special use-case: run an outgoing call scenario within particular app. Voximplant requires a rule for that, so rule will be reated automatically.

```sh

$ voximplant start your_app.voximplant.com/test.js

# pass the parameters to the script (json encoded)

$ voximplant start your_app.voximplant.com/test.js --param whattosay --value "Elephants go to the north"

```

## Programmatic usage

Deploy a scenario:

```python
  client.scenarios.add('test.js', path='./path/to/scenario.js')
  
  # or directly upload a code
  
  with open('./path/to/scenario.js') as f:
     client.scenarios.add('test.js', code=f.read())
```

### Run a scenario inside the app

```python
client.scenarios.start('app.client.voximplat.com/test.js')  # app_name/scenario_name
```

### Performing andom queries for the API

```python
skills = client.http.get('GetSkills')

for skill in skills.result:
  print(f"{skill['id']: skill['name']")
  
# upload new skill

client.http.post('AddSkill', dict(
  skill_name='joking',
))
```