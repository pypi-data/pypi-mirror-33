# apispec-clear-unusable

Plugin for apispec which helps reusing the documentation on a muti-endpoint function/method.

## Example with flask-restful

```python
from apispec import APISpec
from flask import Flask, jsonify
from flask_restful import Resource, Api
from marshmallow import Schema, fields

# Create an APISpec
spec = APISpec(
    title='Random swagger Petstore',
    version='1.0.0',
    plugins=[
        'apispec.ext.flask',
        'apispec.ext.marshmallow',
        'brunoais.apispec.ext.clear_unusable',
    ],
)

# This example uses flask but it also works with other frameworks
app = Flask(__name__)
api = Api(app)

class RandomPet(Resource):

    def get(self, species=None, race=None):
        """A cute random furry animal.
        ---
        description: Get a random pet
        parameters:
            - in: path
              name: species
              type: string
              description: The species of the animal to be randomly selected
        parameters:
            - in: path
              name: race
              type: string
              description: The race of the animal to be randomly selected
        responses:
            200:
                description: A pet to be returned
                schema: PetSchema
        """
        return get_random_pet(species=species, race=race), 200


api.add_resource(RandomPet, '/pets/random', endpoint='randompet')
api.add_resource(RandomPet, '/pets/<species>/random', endpoint='randompet_species')
api.add_resource(RandomPet, '/pets/<species>/races/<race>/random', endpoint='randompet_species_race')

spec.definition('Category', schema=CategorySchema)
spec.definition('Pet', schema=PetSchema)

with app.test_request_context():
    spec.add_path(view=random_pet)
```
Output becomes
```
definitions:
	#...
parameters: {}
paths:
  /pets/random:
    get:
      description: Get a random pet
      parameters: []
      responses:
        200:
          description: A pet to be returned
          schema: {$ref: '#/definitions/Pet'}
  /pets/{species}/random:
    get:
      description: Get a random pet
      parameters:
      - {description: The species of the animal to be randomly selected, in: path,
        name: species, required: true, type: string}
      responses:
        200:
          description: A pet to be returned
          schema: {$ref: '#/definitions/Pet'}
  /pets/{species}/races/{race}/random:
    get:
      description: Get a random pet
      parameters:
      - {description: The species of the animal to be randomly selected, in: path,
        name: species, required: true, type: string}
      - {description: The race of the animal to be randomly selected, in: path, name: race,
        required: true, type: string}
      responses:
        200:
          description: A pet to be returned
          schema: {$ref: '#/definitions/Pet'}
swagger: '2.0'
```

## Installation

    pip install apispec-clear-unusable

## License

This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
