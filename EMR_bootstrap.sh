#Install python modules
sudo easy_install pip
sudo pip install -U pip setuptools wheel
sudo cp /usr/local/bin/pip /usr/bin/
sudo pip install Kafka
sudo pip install django


#https://github.com/awslabs/emr-bootstrap-actions/blob/master/R/Hadoop/emR_bootstrap.sh
#Judge if the instance is the master
IS_MASTER=false
if [ -f /mnt/var/lib/info/instance.json ]
then
	IS_MASTER=`cat /mnt/var/lib/info/instance.json | tr -d '\n ' | tr -d '}' | sed -n 's|.*\"isMaster\":\([^,]*\).*|\1|p'`
fi
#Read the file from s3 to hdfs
if [ "$IS_MASTER" = true ]; then
	hdfs dfs -mkdir /user/ds
	hdfs dfs -mkdir /user/ds/airlines
	hdfs dfs -cp s3n://aws-logs-462504581059-us-east-1/data/countries.csv hdfs:///user/ds/countries.csv 
	i=0
	while [ $i -lt 14 ]
	do
		echo $i
		hdfs dfs -cp s3n://aws-logs-462504581059-us-east-1/data/airlines/airlines$i.csv hdfs:///user/ds/airlines/airlines$i.csv
		i=`expr $i + 1`
	done
fi
