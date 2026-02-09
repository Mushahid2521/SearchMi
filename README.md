### SearchMi

This is a simple application that allows the user to identify the set of species/features that differentiates between two groups or cohorts. 

### How to use it?

1. Download the SearchMi.exe file from the dist folder.
2. Run the .exe file.
3. Upload a csv file.
4. Write your metadata column name that contains the group/cohort information.
5. Choose your search algorithm and statistics.
6. Click on the search button.
7. The application will find the set of species/features that differentiates between the two groups or cohorts.
8. Results can be exported in an excel file.
9. A simple visualisation is also added to see the differentiation between the two groups.

### How to rebuild the .exe file?

1. Open the project and make your changes.
2. Open the terminal and run the command: 

```
pyinstaller main.spec
````
