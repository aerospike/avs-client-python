#!/bin/bash

function generate_derivative_certs() {

	openssl genrsa -out $1.key 2048
	openssl rsa -in $1.key -out $1.key.pem
	openssl rsa -aes256 -in $1.key.pem -out $1.key.encrypted.pem -passout file:tls/storepass

	openssl req -new -sha256 -key $1.key.pem -subj "/C=IN/ST=KA/O=Aerospike, Inc./CN=$1" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf  <(printf "\n[SAN]\nsubjectAltName=DNS:$1,DNS:*.$1")) -out $1.csr

	openssl x509 -req -in $1.csr -CA $root_certificate_path -CAkey $root_certificate_key_path -CAcreateserial -out $1.crt -days 3650 -sha256 -extensions SAN -extfile <(cat /etc/ssl/openssl.cnf  <(printf "\n[SAN]\nsubjectAltName=DNS:$1,DNS:*.$1"))

	# export certificate to pkcs12
	openssl pkcs12 -export -out $1.p12 -in $1.crt -inkey $1.key.pem -password file:tls/storepass

	chmod 777 $1.p12

	# import pkcs12 into a keystore
	keytool -importkeystore -srckeystore $1.p12 -destkeystore $1.keystore.jks -srcstoretype pkcs12 -srcstorepass citrusstore -deststorepass citrusstore -noprompt

	openssl x509 -noout -text -in $1.crt

	if [[ "$1" != "$2" ]]; then
		openssl genrsa -out $2.key 2048
		openssl rsa -in $2.key -out $2.key.pem
		openssl rsa -aes256 -in $2.key.pem -out $2.key.encrypted.pem -passout file:tls/storepass

		openssl req -new -sha256 -key $2.key.pem -subj "/C=IN/ST=KA/O=Aerospike, Inc./CN=$2" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf  <(printf "\n[SAN]\nsubjectAltName=DNS:$2,DNS:*.$2")) -out $2.csr

		openssl x509 -req -in $2.csr -CA $root_certificate_path -CAkey $root_certificate_key_path -CAcreateserial -out $2.crt -days 3650 -sha256 -extensions SAN -extfile <(cat /etc/ssl/openssl.cnf  <(printf "\n[SAN]\nsubjectAltName=DNS:$2,DNS:*.$2"))

		# export certificate to pkcs12
		openssl pkcs12 -export -out $2.p12 -in $2.crt -inkey $2.key.pem -password file:tls/storepass

		chmod 777 $2.p12

		# import pkcs12 into a keystore
		keytool -importkeystore -srckeystore $2.p12 -destkeystore $2.keystore.jks -srcstoretype pkcs12 -srcstorepass citrusstore -deststorepass citrusstore -noprompt

		openssl x509 -noout -text -in $2.crt
	fi
}

tls_maybe=""
rbac_maybe=""
root_certificate_maybe=""
root_certificate_name=""
specify_details_maybe=""
openssl_cnf_maybe=""
config=""
password=""
key_pair_maybe=""
key_password=""
mutual_auth_maybe=""
client_name=""
server_name=""
port=""
host=""


while [[ $# -gt 0 ]]; do
    case $1 in
        --tls_maybe)
            tls_maybe="$2"
            shift 2
            ;;
        --rbac_maybe)
            rbac_maybe="$2"
            shift 2
            ;;
        --root_certificate_maybe)
            root_certificate_maybe="$2"
            shift 2
            ;;
        --root_certificate_name)
            root_certificate_name="$2"
            shift 2
            ;;
        --specify_details_maybe)
            specify_details_maybe="$2"
            shift 2
            ;;
        --openssl_cnf_maybe)
            openssl_cnf_maybe="$2"
            shift 2
            ;;
        --config)
            config="$2"
            shift 2
            ;;
        --password)
            password="$2"
            shift 2
            ;;
        --key_pair_maybe)
            key_pair_maybe="$2"
            shift 2
            ;;
        --key_password)
            key_password="$2"
            shift 2
            ;;
        --mutual_auth_maybe)
            mutual_auth_maybe="$2"
            shift 2
            ;;
        --client_name)
            client_name="$2"
            shift 2
            ;;
        --server_name)
            server_name="$2"
            shift 2
            ;;          
        --port)
            port="$2"
            shift 2
            ;;
        --host)
            host="$2"
            shift 2
            ;;   

        *)
            echo "Unknown parameter passed: $1"
            exit 1
            ;;
    esac
done


echo "Final values:"
echo "tls_maybe: $tls_maybe"
echo "rbac_maybe: $rbac_maybe"
echo "root_certificate_maybe: $root_certificate_maybe"
echo "root_certificate_name: $root_certificate_name"
echo "specify_details_maybe: $specify_details_maybe"
echo "openssl_cnf_maybe: $openssl_cnf_maybe"
echo "config: $config"
echo "password: $password"
echo "key_pair_maybe: $key_pair_maybe"
echo "key_password: $key_password"
echo "mutual_auth_maybe: $mutual_auth_maybe"
echo "client_name: $client_name"
echo "server_name: $server_name"
echo "port: $port"
echo "host: $host"


rm -rf tls
mkdir -p tls
mkdir -p tls/jwt
cp assets/aerospike-proximus.yml aerospike-proximus.yml
cp assets/aerospike.conf aerospike.conf
cp assets/features.conf features.conf

echo "Welcome to the AVS Configuration generator"

if [[ "$tls_maybe" == "" ]]; then

	read -p "Would you like to configure your server for TLS? (y/n): " tls_maybe
fi

if [[ "$tls_maybe" != "y" && "$tls_maybe" != "n" ]]; then
    echo "INVALID INPUT: must enter 'y' or 'n' "
    exit 1
fi

if [[ "$rbac_maybe" == "" ]]; then

	read -p "Would you like to configure your server for Role-Based Access Control? (y/n): " rbac_maybe
fi

if [[ "$rbac_maybe" != "y" && "$rbac_maybe" != "n" ]]; then
    echo "INVALID INPUT: must enter 'y' or 'n' "
    exit 1
fi

if [[ "$rbac_maybe" == "y" ]]; then
    if [[ "$tls_maybe" == "n" ]]; then
        echo "INVALID CONFIGURATION: TLS is required when using Role-Based Access Control"
        exit 1
    fi
fi



if [[ "$tls_maybe" == "y" ]]; then
	if [[ "$root_certificate_maybe" == "" ]]; then

		read -p "Do you want to generate a root certificate? (y/n): " root_certificate_maybe
	fi
	if [[ "$root_certificate_maybe" == "y" ]]; then
		if [[ "$root_certificate_name" == "" ]]; then

			read -p "What would you like the root certificate prefix to be " root_certificate_name
		fi
		if [[ "$specify_details_maybe" == "" ]]; then

			read -p "Do you want to specify details for certificate generation? (y/n): " specify_details_maybe
		fi

		if [[ "$specify_details_maybe" == "y" ]]; then
			read -p "Country Name (2 letter code) [AU]: " country
			read -p "State or Province Name (full name) [Some-State]: " state
			read -p "Locality Name (eg, city) []: " city
			read -p "Organization Name (eg, company) [Internet Widgits Pty Ltd]: " organization
			read -p "Organizational Unit Name (eg, section) []: " unit
			read -p "Common Name (e.g. server FQDN or YOUR name) []: " common_name
			read -p "Email Address []: " email
		fi

		if [[ "$specify_details_maybe" != "n" ]]; then
			echo "INVALID INPUT: 'y' or 'n' required"
			exit 1
		fi


		country=${country:-US}
		state=${state:-SD}
		city=${city:-Spearfish}
		organization=${organization:-Aerospike}
		unit=${unit:-$Client SDK Team}
		common_name=${common_name:-aerospike-proximus}
		email=${email:-dpelini@aerospike.com}

		subj="/C=$country/ST=$state/L=$city/O=$organization/OU=$unit/CN=$common_name/emailAddress=$email"

		echo $root_certificate_name
		openssl genrsa -out $root_certificate_name.key 2048
		openssl rsa -in $root_certificate_name.key -out $root_certificate_name.key.pem

		# Generate a new self-signed certificate
		openssl req -new -x509 -key $root_certificate_name.key.pem -out $root_certificate_name.crt -days 3650 -sha256 -subj "$subj"

		if [[ "$openssl_cnf_maybe" == "" ]]; then

			read -p "Would you like to specify an openssl configuration file" openssl_cnf_maybe

		fi
		
		if [[ "$openssl_cnf_maybe" == "y" ]]; then
			if [[ "$config" == "" ]]; then

				read -p "What is the path of the config file" config
			
			fi


		elif [[ "$openssl_cnf_maybe" == "n" ]]; then
			config="assets/template.cnf"
		else
			echo "INVALID INPUT: 'y' or 'n' required"
			exit 1
		fi
		openssl req -config $config \
		      -key $root_certificate_name.key.pem \
		      -new -x509 -days 7300 -sha256 -extensions v3_ca \
		      -out $root_certificate_name.cert.pem \
		      -subj "$subj"

		if [[ "$password" == "" ]]; then

			read -sp "Set the password for the keystore/truststore file: " password
		fi

		touch tls/storepass
		touch tls/keypass

		chmod 777 tls/storepass
		chmod 777 tls/keypass

		echo $password > tls/storepass
		echo $password > tls/keypass

		keytool -import -file $root_certificate_name.crt --storepass citrusstore -keystore $root_certificate_name.truststore.jks -alias $root_certificate_name -noprompt
		openssl x509 -noout -text -in $root_certificate_name.cert.pem

		root_certificate_path=$root_certificate_name.crt
		root_certificate_key_path=$root_certificate_name.key.pem





	elif [[ "$root_certificate_maybe" == "n" ]]; then
		if [[ "$root_certificate_path" == "" ]]; then

			read -p "What is the path of your pre-generated root_certificate: " root_certificate_path

		fi
		if [[ "$root_certificate_key_path" == "" ]]; then

			read -p "What is the path of your pre-generated root_certificate key: " root_certificate_key_path
		fi
	else
		echo "BRUHHHHHINVALID INPUT: 'y' or 'n' required"
		exit 1
	fi	

	if [[ "$rbac_maybe" == "y" ]]; then
		if [[ "$key_pair_maybe" == "" ]]; then
			read -p "Do you want to generate a key pair? (y/n): " key_pair_maybe

			if [[ "$key_password" == "" ]]; then
				read -sp "Enter a password for your keypair? (y/n): " key_password
			fi

		fi

		if [[ "$key_pair_maybe" == "y" ]]; then
			echo $key_password
			openssl genpkey -algorithm RSA -out tls/jwt/private_key.pem -pkeyopt rsa_keygen_bits:2048
			openssl rsa -in tls/jwt/private_key.pem -pubout -out tls/jwt/public_key.pem

			chmod 777 tls/jwt/private_key.pem
			chmod 777 tls/jwt/public_key.pem

			security_stanza=$(cat <<EOF
security:
  auth-token:
    private-key: /etc/aerospike-proximus/tls/jwt/private_key.pem
    public-key: /etc/aerospike-proximus/tls/jwt/public_key.pem
    token-expiry: 300_000
EOF
)

			sed -i '96,100d' "aerospike-proximus.yml"

			echo "$security_stanza" | envsubst >  "assets/security_stanza.txt"


			sed -i '95r assets/security_stanza.txt' aerospike-proximus.yml

		fi
	fi
	if [[ "$mutual_auth_maybe" == "" ]]; then
		read -p "Would you like to enable mutual authentication TLS? (y/n): " mutual_auth_maybe
	fi

	if [[ "$mutual_auth_maybe" == "y" ]]; then
		if [[ "$client_name" == "" ]]; then
			read -p "What would you like the client prefix to be " client_name
		fi
		if [[ "$server_name" == "" ]]; then

			read -p "What would you like the server prefix to be " server_name
		fi

        generate_derivative_certs "$client_name" "$server_name"

		tls_stanza=$(cat <<EOF
tls:
  service-tls:
    trust-store:
      store-file: /etc/aerospike-proximus/tls/$root_certificate_name.truststore.jks 
      store-password-file: /etc/aerospike-proximus/tls/storepass
    key-store:
      store-file: /etc/aerospike-proximus/tls/$server_name.keystore.jks
      store-password-file: /etc/aerospike-proximus/tls/storepass
      key-password-file: /etc/aerospike-proximus/tls/keypass
    mutual-auth: true
    # Client certificate subject names that are allowed
    allowed-peer-names:
      - $client_name
EOF
)

		sed -i '15,27d' "aerospike-proximus.yml"

		echo "$tls_stanza" | envsubst > "assets/tls_stanza.txt"

		sed -i '14r assets/tls_stanza.txt' aerospike-proximus.yml

		if [[ "$port" == "" ]]; then
			read -p "Specify a port address:" port

		fi

		service_stanza=$(cat <<EOF
      tls-id: service-tls

      # Required when running behind NAT
      advertised-listeners:
        default:
          # List of externally accessible addresses and
          # ports for this Proximus instance.
          - address: $server_name
            port: $port

EOF
)

		sed -i '56,65d' "aerospike-proximus.yml"

		echo "$service_stanza" | envsubst > "assets/service_stanza.txt"

		sed -i '55r assets/service_stanza.txt' aerospike-proximus.yml
		if [[ "$host" == "" ]]; then
			read -p "Specify a host address:" host

		fi
		line="$host $server_name"


		# Check if the line exists in /etc/hosts
		if ! grep -qF "$line" /etc/hosts; then
		    # Add the line to /etc/hosts
		    echo "$line" | sudo tee -a /etc/hosts > /dev/null
		    echo "Entry added to /etc/hosts."
		fi

	elif [[ "$mutual_auth_maybe" == "n" ]]; then
  		generate_derivative_certs "child" "child"


		tls_stanza=$(cat <<EOF
tls:
  service-tls:
    trust-store:
      store-file: /etc/aerospike-proximus/tls/$root_certificate_name.truststore.jks 
      store-password-file: /etc/aerospike-proximus/tls/storepass
    key-store:
      store-file: /etc/aerospike-proximus/tls/child.keystore.jks
      store-password-file: /etc/aerospike-proximus/tls/storepass
      key-password-file: /etc/aerospike-proximus/tls/keypass
    #mutual-auth: true
    # Client certificate subject names that are allowed
    #allowed-peer-names:
    #  - child
EOF
)
		sed -i '15,27d' "aerospike-proximus.yml"

		echo "$tls_stanza" | envsubst > "assets/tls_stanza.txt"

		sed -i '14r assets/tls_stanza.txt' aerospike-proximus.yml
		if [[ "$port" == "" ]]; then
			read -p "Specify a port address:" port

		fi

		service_stanza=$(cat <<EOF
      tls-id: service-tls

      # Required when running behind NAT
      #advertised-listeners:
      #  default:
          # List of externally accessible addresses and
          # ports for this Proximus instance.
      #    - address: child
      #      port: $port
EOF
)

		sed -i '56,65d' "aerospike-proximus.yml"

		echo "$service_stanza" | envsubst >  "assets/service_stanza.txt"
		sed -i '55r assets/service_stanza.txt' aerospike-proximus.yml




		if [[ "$host" == "" ]]; then
			read -p "Specify a host address:" host

		fi
		line="$host $server_name"


		# Check if the line exists in /etc/hosts
		if ! grep -qF "$line" /etc/hosts; then
		    # Add the line to /etc/hosts
		    echo "$line" | sudo tee -a /etc/hosts > /dev/null
		    echo "Entry added to /etc/hosts."
		fi
	fi
fi



shopt -s extglob  # Enable extended globbing

mv !(tls|assets|rbac|standard|requirements.txt|setup.py|utils.py|__init__.py|siftsmall) tls/

mv tls/gen.sh gen.sh

mv tls/aerospike-proximus.yml aerospike-proximus.yml

mv tls/aerospike.conf aerospike.conf

mv tls/features.conf features.conf

