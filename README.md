
<body>
<h1>Data Pipelines with Apache Airflow</h1>

<h2>The Story</h2>
<p>A music streaming company, Sparkify, has decided that it is time to introduce more automation and monitoring to their data warehouse ETL pipelines and come to the conclusion that the best tool to achieve this is Apache Airflow.</p>
<p>They have decided to bring you into the project and expect you to create high-grade data pipelines that are dynamic and built from reusable tasks, can be monitored, and allow easy backfills. They have also noted that data quality plays a big part when analyses are executed on top of the data warehouse and want to run tests against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.</p>
<p>The source data resides in S3 and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.</p>

<h2>The ETL DAG</h2>
<p>The ETL DAG is composed of the following tasks:</p>
<ul>
    <li><strong>Begin_execution:</strong> Initialize the pipeline.</li>
    <li><strong>Staging tasks:</strong> Copy data from S3 to staging tables in Redshift. <em>Stage_songs</em> and <em>Stage_events</em> tasks are run in parallel.</li>
    <li><strong>Load fact table task:</strong> Load the songplays fact table in Redshift.</li>
    <li><strong>Load dimension tables tasks:</strong> Load dimension tables in Redshift. <em>Load_user_dim_table</em>, <em>Load_artist_dim_table</em>, <em>Load_song_dim_table</em>, and <em>Load_time_dim_table</em> tasks are run in parallel.</li>
    <li><strong>Run data quality checks task:</strong> Run checks to ensure data quality.</li>
    <li><strong>Stop execution:</strong> Mark the end of the pipeline.</li>
</ul>

<h2>Project Structure</h2>
<pre>
├── LICENSE
├── README.md
├── create_tables.sql
├── assets
│   ├── screenshots
├── dags
│   ├── main.py
├── docker-compose.yaml
└── plugins
    ├── __init__.py
    ├── helpers
    │   ├── __init__.py
    │   └── sql_queries.py
    └── operators
        ├── __init__.py
        ├── data_quality.py
        ├── load_dimension.py
        ├── load_fact.py
        └── stage_redshift.py
</pre>

<h3>docker-compose.yaml</h3>
<p>Runs Airflow locally using Docker.</p>

<h3>create_tables.sql</h3>
<p>SQL script that can be used to create all the required tables in Redshift.

<h3>The dags/ directory</h3>
<ul>
    <li><strong>main.py:</strong> This is the main DAG where all the steps of the ETL are performed.</li>
    <li><strong>create_tables_dag.py:</strong> A helper DAG that can be used to create all the tables. Alternatively, one can run the script <em>create_tables.sql</em> in the Redshift cluster to set all the tables.</li>
</ul>

<h3>The plugins/ directory</h3>
<p>This directory contains the <em>operators</em> and <em>helpers</em> subdirectories.</p>

<h4>plugins/operators</h4>
<p>Subpackage in which the reusable custom operators are defined.</p>
<ul>
    <li><strong>stage_redshift.py:</strong> Defines the operator <em>StageToRedshiftOperator</em> that is used to copy data from a S3 path to staging tables in Redshift.</li>
    <li><strong>load_fact.py:</strong> Defines the operator <em>LoadFactOperator</em> that is used to load the fact table songplays using the staging tables.</li>
    <li><strong>load_dimension.py:</strong> Defines the operator <em>LoadDimensionOperator</em> that is used to load the dimension tables songs, artists, users, and time.</li>
    <li><strong>data_quality.py:</strong> Defines the operator <em>DataQualityOperator</em> that is used to run data quality checks at the last step of the ETL.</li>
</ul>

<h4>plugins/helpers</h4>
<p><em>sql_queries.py</em>: Defines the insert queries and the create table queries that are used by the <em>LoadDimensionOperator</em> and the <em>CreateTableOperator</em>, respectively.</p>

<h2>Running the Project</h2>
<p>It is necessary to have an AWS account, Docker, and Docker Compose installed to run the Project.</p>

<h3>Setting AWS</h3>
<ol>
    <li>Create a user and attach the policies <em>AmazonRedshiftFullAccess</em> and <em>AmazonS3FullAccess</em> to them. Allow the user to connect to AWS using an access key. We will set up a connection to AWS within Airflow using these credentials.</li>
    <li>Create a Redshift service role and attach the <em>AmazonS3FullAccess</em> policy to it.</li>
    <li>Create a Redshift cluster in AWS and associate the Redshift service role to it.</li>
</ol>

<h3>Running Airflow in Docker</h3>
<p>Run the command in the Project root directory:</p>
<pre>$ docker-compose up -d</pre>
<p>This launches many services. We will shortly describe only Airflow Webserver and Airflow Scheduler.</p>

<h4>Airflow WebServer</h4>
<p>Can be accessed in your web browser at <a href="http://localhost:8080">http://localhost:8080</a>. To log in, use <em>airflow</em> as username and password. From the web UI one can execute the DAGs, add connections to AWS and to Redshift, set variables, and more.</p>
<p><strong>Important:</strong></p>
<ul>
    <li>A connection to AWS must be set using <em>aws_credentials</em> as the connection ID.</li>
    <li>A connection to the Redshift cluster must be set using <em>redshift</em> as the connection ID.</li>
</ul>

<h4>Airflow Scheduler</h4>
<p>The scheduler monitors all tasks and DAGs, then triggers the task instances once their dependencies are complete.</p>

<h2>The Airflow UI</h2>
<p>The Airflow UI can be accessed at <a href="http://localhost:8080">http://localhost:8080</a>.</p>
<p><strong>Username:</strong> airflow</p>
<p><strong>Password:</strong> airflow</p>

<h3>Connect Airflow to AWS</h3>
<p>First, we need to pass to Airflow the AWS credentials and the Redshift connection data.</p>

<h4>AWS Credentials</h4>
<p>Click on the <em>Admin</em> tab and select <em>Connections</em>.</p>
<p>Under Connections, select <em>Create</em>.</p>
<p>On the create connection page, enter the following values:</p>
<ul>
    <li><strong>Connection Id:</strong> aws_credentials</li>
    <li><strong>Connection Type:</strong> Amazon Web Services</li>
    <li><strong>AWS Access Key ID:</strong> Access key ID from the IAM User credentials</li>
    <li><strong>AWS Secret Access Key:</strong> Secret access key from the IAM User credentials</li>
</ul>
<p>Once you've entered these values, select <em>Save and Add Another</em>.</p>

<h4>Redshift</h4>
<p>On the create connection page, enter the following values:</p>
<ul>
    <li><strong>Connection Id:</strong> redshift</li>
    <li><strong>Connection Type:</strong> Amazon Redshift</li>
    <li><strong>Host:</strong> Redshift cluster endpoint</li>
    <li><strong>Database:</strong> dev</li>
    <li><strong>User:</strong> awsuser</li>
    <li><strong>Password:</strong> Enter the password you created when launching your Redshift cluster</li>
    <li><strong>Port:</strong> 5439</li>
</ul>
<p>Once you've entered these values, select <em>Save</em>.</p>

<h3>Run the DAG</h3>
<p>Click on the <em>final_project</em> and then trigger the DAG by clicking on the play button.</p>
<p>The whole pipeline should take less than 5 minutes to complete.</p>

![Descripción de la imagen](ruta_de_la_imagen)


![Descripción de la imagen](ruta_de_la_imagen)



![Descripción de la imagen](ruta_de_la_imagen)




</body>
</html>
