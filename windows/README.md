# Canvas Development - Generating Course Files

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for generating the cours files. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Functional requirements include Python 3 and pip (Python package manager) as well as Google Chrome(any recent version) installed on your machine before hand. 

These are the python packages you would need before running the script.
- canvasapi
- webdriver-manager
- selenium
- selenium-wire

Download these modules by doing
```
pip install <package-name>
```

### Retrieving the Access Token:
To run this code and generate course files, a canvas access token is required. Go to your account settings and click on new access token button in the Approved Integrations section. Give any name, set the date and time as you wish and save the provided value somwehere. This has to be given to the program as an input.

### Setting up the configuration(Optional)

By default, the course files are generated in the D:/ drive. If you want to get the folder in some other location, change the ```parent_dir``` to your desired location in line 75 of coursefiles.py.


## Running the file

Run the python file. It will first ask for your access token. Then it will ask for the course url for the which you want the course files. Copy paste the course url from your browser and ensure that it is in the following format before entering:
```
https://hulms.instructure.com/courses/1706
```

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc