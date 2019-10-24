from frontend.site.models_site import contact_us

# Create your services here.
def add_contact_us(name, email, phone, message):
	try:
		contact 		= contact_us(
										name = name,
										email = email,
										phone = phone,
										message = message
									)
		contact.save()
		return True
	except Exception as e:
		return False



