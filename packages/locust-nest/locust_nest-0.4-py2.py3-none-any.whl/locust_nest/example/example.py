from locust import TaskSet, task, HttpLocust


class ExampleModel(TaskSet):
    weight = 0
    auth_endpoint = ''
    auth_header = {'Authorization': 'Bearer {}'}
    username = None
    password = None

    def login(self, username, password, auth_endpoint):
        if not auth_endpoint:
            print("No Login required for this Locust")
            return True
            
        payload = {
            'userName': username,
            'password': password
        }
        headers = {'Content-Type': 'application/json'}
        r = self.client.post(auth_endpoint, headers=headers, json=payload)
        if r.ok:
            jr = r.json()
            self.token = jr.get('token')
            return True
        else:
            print(r.content)
            r.raise_for_status()
            return False

    def on_start(self):
        """Set up before running tasks.

        For example:
        * Log in & save token
        * Retrieve bulk information needed for other tasks

        """
        return self.login(self.username, self.password, self.auth_endpoint)

    def on_stop(self):
        """Teardown: unclaim resources e.g. claimed user/resource.

        """

        return

    # task decorator with relative weight of executing the task
    @task(5)
    def model_action(self):
        """Codified behaviour of a particular action this model may perform
        e.g. viewing user details

        """
        self.client.get("/")
        return


class ExampleModelLocust(HttpLocust):
    host = "http://127.0.0.1:8089"
    task_set = ExampleModel
