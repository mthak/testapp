curl -L https://www.opscode.com/chef/install.sh | bash

chef-solo -v
cd
mkdir .chef
echo 'cookbook_path [ "/root/chef-repo/cookbooks" ]' > .chef/knife.rb

echo 'file_cache_path "/root/chef-solo"' >> solo.rb
echo 'cookbook_path "/root/chef-repo/cookbooks"' >> solo.rb

echo '
{
    "run_list": [
        "recipe[java]",
        "recipe[tomcat]"
    ],
    "java": {
        "install_flavor": "oracle",
        "jdk_version": "8",
        "oracle" : {
            "accept_oracle_download_terms": "true"
        }
      },
     "tomcat": {
        "port": 9000
    }
}' > web.json

mkdir -p /root/chef-repo/cookbooks

cd /root/chef-repo/cookbooks

knife cookbook site download java
knife cookbook site download tomcat
knife cookbook site download apt
knife cookbook site download yum
knife cookbook site download yum-epel
knife cookbook site download chef-sugar
knife cookbook site download openssl
knife cookbook site download windows


for file in *.gz; do tar zxf $file; done;

rm -f *.gz

cd

chef-solo -c solo.rb -j web.json
