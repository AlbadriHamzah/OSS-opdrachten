import csv
import os
import pwd
import grp
import subprocess

def create_users(csv_file):
    # Studenten en klassengroepen maken
    student_group = 'students'
    class_groups = set()

    # Controleer of de studentengroep al bestaat, zo niet, maak deze aan
    try:
        grp.getgrnam(student_group)
    except KeyError:
        subprocess.run(['groupadd', student_group], check=True)

    # Open het CSV-bestand en lees de gegevens in
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            class_group = row['klasgroep']
            class_groups.add(class_group)
            username = 's' + row['student_id']

            # Controleer of de gebruiker al bestaat, zo ja, sla deze over
            try:
                pwd.getpwnam(username)
                print(f"Gebruiker {username} bestaat al, wordt overgeslagen")
            except KeyError:
                home_dir = f"/home/{row['email'].split('@')[0]}"

                # Maak de gebruiker aan met de juiste opties en parameters
                subprocess.run(['useradd', '-m', '-d', home_dir, '-s', '/bin/bash', '-c', row['full_name'], username], check=True)
                subprocess.run(['usermod', '-aG', student_group, username], check=True)
                subprocess.run(['usermod', '-aG', class_group, username], check=True)

                # Controleer of er een wachtwoord is opgegeven en stel deze in
                if row['wachtwoord']:
                    subprocess.run(['chpasswd'], input=f"{username}:{row['wachtwoord']}\n", universal_newlines=True, check=True)

                # Controleer of er een SSH-public key is opgegeven en voeg deze toe
                if 'ssh_public_key' in row:
                    ssh_dir = os.path.join(home_dir, '.ssh')
                    os.makedirs(ssh_dir, exist_ok=True)
                    with open(os.path.join(ssh_dir, 'authorized_keys'), 'a') as f:
                        f.write(f"{row['ssh_public_key']}\n")

    # Maak de klassengroepen aan als deze nog niet bestaan
    for group in class_groups:
        try:
            grp.getgrnam(group)
        except KeyError:
            subprocess.run(['groupadd', group], check=True)

if __name__ == '__main__':
    create_users('studenten.csv')
