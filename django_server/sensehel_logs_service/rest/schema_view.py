from rest_framework.schemas import get_schema_view
from rest_framework.schemas.openapi import SchemaGenerator

schema_description = """
The SenseHel Logger Service (<https://lompakko.ilmastoviisaat.fi>) is an example service integrating with the 
SenseHel platform (<https://oma.ilmastoviisaat.fi>). The service illustrates how data gathered by the **platform**
is disseminated to external **services** based on **subscriptions** initiated by the platform users, and how the 
services are then expected to utilize that data to generate **reports** available to the users through the platform
UI.

The logger service source code is available at <https://github.com/ForumViriumHelsinki/SenseHelLogs>; the latest
version of this documentation should always be available at <https://lompakko.ilmastoviisaat.fi/swagger-ui/>.

This service is implemented for two purposes:

 - Allowing citizens participating in the Climate Smart Housing Companies project to view 
   and analyze the data gathered in their own apartments
 - Serving as an example for other services to be implemented in the project.

The SenseHel Logger Service provides the following actions:

 - **Create subscription**: Create service subscriptions, specifying what data (e.g. temperature, humidity)
   will be provided for the subscription.
 - **Submit data**: Provide data points for the subscription.
 - **Unsubscribe**, which also deletes all gathered data for the subscription from the database.

In addition to the data API, the service provides 2 HTML report views:

 - **Subscription Report**: HTML report for the subscription, to be viewed as a standalone page. 
   The SenseHel UI will provide a link to this view to the subscriber on the main page. The full UI allows 
   choosing time period, viewing plots and exporting data as csv.
 - **Subscription Preview**: HTML report for the subscription, to be embedded in the SenseHel UI as an iframe. 
   The preview provides a plot of the last 24 hours of data.
"""


class CustomSchemaGenerator(SchemaGenerator):
    ui_paths = {
        '/': {
            'get': {
                'operationId': 'Subscription Report',
                'description': (
                    'HTML report for the subscription, to be viewed as a standalone page. ' +
                    'The SenseHel UI will provide a link to this view to the subscriber on the main page.'),
                'tags': ['Subscription Reports'],
                "parameters": [
                    {
                        "name": "uuid",
                        "in": "query",
                        "required": True,
                        "description": "UUID of the subscription",
                        "schema": {
                            "type": "string"
                        }
                    }
                ]
            }
        },
        '/preview/': {
            'get': {
                'operationId': 'Subscription Preview',
                'description': 'HTML report for the subscription, to be embedded in the SenseHel UI as an iframe.',
                'tags': ['Subscription Reports'],
                "parameters": [
                    {
                        "name": "subscription",
                        "in": "query",
                        "required": True,
                        "description": "UUID of the subscription",
                        "schema": {
                            "type": "string"
                        }
                    }
                ]
            }
        }
    }

    def get_paths(self, request=None):
        return dict(super().get_paths(request), **self.ui_paths)


schema_view = get_schema_view(
    title="SenseHel Logger Service API",
    description=schema_description,
    version="1.0.0",
    public=True,
    generator_class=CustomSchemaGenerator
)
