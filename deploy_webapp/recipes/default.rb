#
# Cookbook Name:: deploy_webapp
# Recipe:: default
#
# Copyright 2015, YOUR_COMPANY_NAME
#
# All rights reserved - Do Not Redistribute
#
#
source_url = "http:github.nexus.com#{node[:app][:groupid]}&a=#{node[:tcat][:war_name]}&e=war&v=LATEST"

bash "delete_files" do
   cwd "/local_app/repo"
   code <<-EOS
   pwd
   rm -f *
   echo " files removedand moved to backup folder now " 
   ls 
   EOS
end

directory "/local_app/repo" do
  owner "deploy"
  group "deploy"
  mode 0755
  recursive true
  action :create
end


remote_file "/local_app/repo/#{node[:tcat][:war_name]}.war" do
  source "#{source_url}"
  mode 0777
  owner "deploy"
  group "deploy"
  action :create
end

remote_file "/local_app/repo/#{node[:tcat][:env]}-config.zip" do
  source "http:github.nexus#{node[:tcat][:env]}-config&c=bin&e=zip&v=LATEST"
  mode '777'
  owner "deploy"
end

bash "unzip_file" do
   cwd "/local_app/repo"
   code <<-EOS
  set -e  -x
   pwd
   rm -rf "#{node[:tcat][:env]}-config"
   unzip -o #{node[:tcat][:env]}-config.zip -d /local_app/
   EOS
end

service tomcat8 do
service_name tomcat8 
action: stop
done

## Setup and start  all services one by one
## this loop below will install fresh tomcat and service




Chef::Log.info " installing webapp on "
bash "install_webapp" do
 cwd "#{node['tcat']['prefix']}/webapps"
 code <<-EOS
cp -f /local_app/repo/#{node[:tcat][:war_name]}.war  #{node['tcat']['prefix']}/webapps/#{node[:tcat][:war_name]}.war
 EOS
done
