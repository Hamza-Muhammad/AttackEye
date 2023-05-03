
# # !/bin/sh
# # export PATH=$PATH:home/hamza/snap/bin


#export PATH=$PATH:/usr/local/go/bin/
# #export PATH=$PATH:/root/go/pkg/mod/bin

# # export PATH=$PATH:/root/go/pkg/mod/pkg/mod/github.com/OWASP/Amass/v3/cmd/amass
# # cd /root/go/pkg/mod/pkg/mod/github.com/OWASP/Amass/v3/cmd/amass
#export PATH=$PATH:/home/$USER/django-rest-api/django-rest-api-master/go/pkg/mod/pkg/mod/github.com/OWASP/Amass/v3/cmd/amass
#cd /home/$USER/django-rest-api/django-rest-api-master/go/pkg/mod/pkg/mod/github.com/OWASP/Amass/v3/cmd/amass
# var a=$1
# echo $a
# echo "******************************HHHHHHHHHHHHHHH HHHHHHHHHHHHHHHH***************************"
# echo $1
# ./amass enum -passive -d $1 -o /home/hamza/django-rest-api/django-rest-api-master/DjangoRestApi/attackeye/templates/$1.txt 

# parent_dir="$(dirname -- "$(realpath -- "$0")")"
parent_dir=$(realpath -- "/home/$USER/nmapintegrate/AttackEye")
cd $parent_dir/go/pkg/mod/pkg/mod/github.com/OWASP/Amass/v3/cmd/amass

./amass enum -d $1 -o $parent_dir/attack_eye/apps/amass/generated_subdomains/$1.txt

./amass viz -enum 1 -graphistry -d $1 
# # mv amass_graphistry.json /home/nccs-irp/sigma.js/examples/layouts/data.json
mv amass_graphistry.json $parent_dir/attack_eye/apps/amass/generated_subdomains/$1
