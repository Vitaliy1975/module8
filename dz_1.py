from collections import UserDict
import pickle
import re
import datetime

class Field:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)

class Name(Field):
		pass

class Phone(Field):
    def check_if_10(self):
        length=self
        if len(length)!=10:
            raise Exception("Wrong phone number format. Should be 10 digits.")
        else:
            return self
              
class Birthday(Field):
    def check_birthday_format(self):
        pattern=r"[0-3]\d\.[0-1]\d\.\d\d\d\d"
        if re.match(pattern,self):
            try:
                bday=datetime.datetime.strptime(self,"%d.%m.%Y").date()
            except Exception as e:
                raise e
            return bday
        raise Exception("Invalid date format. Use DD.MM.YYYY")

class Record():
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday=None

    def add_birtday(self,item:Birthday):
        try:
            self.birthday=Birthday.check_birthday_format(item)
        except Exception as e:
            print(e)

    def add_phone(self,item):
        try:
            self.phones.append(str(Phone.check_if_10(item)))
        except Exception as e:
            print(e)
        
    def remove_phone(self,item):
        if item in self.phones:
            self.phones.remove(item)
    
    def edit_phone(self,old,new):
        if old in self.phones:
            self.phones.remove(old)
            try:
                self.phones.append(str(Phone.check_if_10(new)))
            except Exception as e:
                print(e)
            # return f"{self.name.value}:{'; '.join(p for p in self.phones)}"
        
    def find_phone(self,phone):
        if phone in self.phones:
            return f"{self.name}: {phone}"
        else:
            return "Not found"
    
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p for p in self.phones)}"#, birthday: {self.birthday}"
    
    def return_dict(self):
        return {'name':self.name.value,'phones':self.phones,'birthday':self.birthday}

class AddressBook(UserDict):
    def add_record (self,item:Record):
        self.data[item.name.value]=item
        # self.data.update(item.name.value)
    
    def find(self,item):
        return self.data.get(item)
            
    def delete(self,item):
        if item in self.data:
            del self.data[item]

    def show_birthday(self,item:Record):
        d=self.data[item].return_dict()
        k=d.get("name")
        v=d.get("birthday")
        return f"{k} : {v}"
    
    def birthdays(self,book):
        users=[]
        for _,j in book.data.items():
            a=j.return_dict()
            if a["birthday"]: 
                users.append(a)
        congratulation_list=[]
        today_date=datetime.datetime.today().date()
        today_year=today_date.year
        today_year_string=str(today_year)
        for user in users:
            # birthday=datetime.datetime.strptime(user["birthday"],"%Y.%m.%d").date()
            birthday_noyear_string=(user["birthday"]).strftime("%m.%d")
            birthday_this_year_string=today_year_string+"."+birthday_noyear_string
            birthday_this_year=datetime.datetime.strptime(birthday_this_year_string,"%Y.%m.%d").date()
            weekday=birthday_this_year.weekday()
            difference=birthday_this_year-today_date
            if difference.days<0:
                birthday_next_year_string=str(int(today_year_string)+1)+"."+birthday_noyear_string
                congratulation_list.append({"name":user["name"],"congratulation_date":("Next year birthday "+birthday_next_year_string)})
                continue
            elif difference.days>7:
                continue
            elif weekday==6:
                bday_monday=birthday_this_year+datetime.timedelta(days=1)
                congratulation_list.append({"name":user["name"],"congratulation_date":(datetime.datetime.strftime(bday_monday,"%Y.%m.%d"))})
                continue
            elif weekday==5:
                bday_monday=birthday_this_year+datetime.timedelta(days=2)
                congratulation_list.append({"name":user["name"],"congratulation_date":(datetime.datetime.strftime(bday_monday,"%Y.%m.%d"))})
                continue
            else:
                            congratulation_list.append({"name":user["name"],"congratulation_date":birthday_this_year_string})
        return congratulation_list
    
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "No such name. Input correct name, please."
        except IndexError:
            return "Enter the argument for the command."
    return inner

@input_error
def add_contact(args, book:AddressBook):
    name, phone = args
    new_record=Record(name)
    new_record.add_phone(phone)
    book.add_record(new_record)
    return "Contact added."

@input_error
def change_contact(args,book:AddressBook):
    if len(args)==3:
        name,phoneold,phonenew=args
        nname=book.find(name)
        nname.edit_phone(phoneold,phonenew)
        return "Contact updated."
    elif len(args)==2:
        name,phone=args
        nname=book.find(name)
        nname.add_phone(phone)
        return "New phone added."

@input_error
def show_phone(args,book:AddressBook):
    name=args[0]
    nname=book.find(name)
    return nname

@input_error
def show_all(book:AddressBook):
    for _,r in book.data.items():
        print(r)

@input_error
def add_birthday(args, book:AddressBook):
    name,birthday=args
    nname=book.find(name)
    nname.add_birtday(birthday)
    book.add_record(nname)
    return "Birthday added."
    # реалізація

@input_error
def show_birthday(args, book:AddressBook):
    name=args[0]
    return book.show_birthday(name)
    # реалізація

@input_error
def birthdays(book:AddressBook):
    return book.birthdays(book)
    # реалізація

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book=load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command=="change":
            print(change_contact(args,book))
        elif command=="phone":
            print(show_phone(args,book))
        elif command=="all":
            show_all(book)
        elif command == "add-birthday":
            print(add_birthday(args,book))
            # реалізація
        elif command == "show-birthday":
            print(show_birthday(args,book))
            # реалізація
        elif command == "birthdays":
            print(birthdays(book))
            # реалізація
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
