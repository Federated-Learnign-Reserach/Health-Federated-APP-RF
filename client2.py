if __name__ == "__main__":
    """ Load Bank Customer churn data from France """
(X_train, y_train), (X_test, y_test) = utils.load_data_client2()

# Split train set into 10 partitions and randomly use one for training.
partition_id = np.random.choice(5)
(X_train, y_train) = utils.partition(X_train, y_train, 5)[partition_id]

"""Create a Logistic Regression Model """
model = LogisticRegression(
    solver='saga',
    penalty="l2",
    max_iter=1,  # local epoch
    warm_start=True,  # prevent refreshing weights when fitting
)

# Setting initial parameters, akin to model.compile for keras models
utils.set_initial_params(model)

""" Define Flower client """


class MnistClient(fl.client.NumPyClient):
    def get_parameters(self):  # type: ignore
        return utils.get_model_parameters(model)

    def fit(self, parameters, config):  # type: ignore
        utils.set_model_params(model, parameters)
        # Ignore convergence failure due to low local epochs
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model.fit(X_train, y_train)
        print(f"Training finished for round {config['rnd']}")
        return utils.get_model_parameters(model), len(X_train), {}

    def evaluate(self, parameters, config):  # type: ignore
        utils.set_model_params(model, parameters)
        preds = model.predict_proba(X_test)
        all_classes = {'1', '0'}
        loss = log_loss(y_test, preds, labels=[1, 0])
        accuracy = model.score(X_test, y_test)
        return loss, len(X_test), {"accuracy": accuracy}


""" Start Flower client """
fl.client.start_numpy_client(
    server_address="localhost:5040",
    client=MnistClient())