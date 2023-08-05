from visma.api import VismaAPI
from pprint import pprint
from visma.models import Customer, CustomerInvoiceDraftRow, CustomerInvoiceDraft

# api = VismaAPI(token_path='auth.json', client_id='pwit', client_secret='SRm9JGgND19pxqOMrL5kabYs6rA4LP3ICrmEvlRQ', test=True)

##customer = api.get_customer(1)
# pprint(api.get_customer_invoice_drafts())

# print(customer.id)
# invoice = CustomerInvoiceDraft.with_customer(customer)

# print(invoice.customer_id)

"""
export VISMA_API_CLIENT_SECRET=SRm9JGgND19pxqOMrL5kabYs6rA4LP3ICrmEvlRQ
export VISMA_API_CLIENT_ID=pwit
export VISMA_API_TOKEN_PATH=/Users/hpw/Documents/Development/visma/visma/auth.json
export VISMA_API_ENV = test
"""

# invoices = CustomerInvoiceDraft.objects.all()
# print(invoices)

customers = Customer.objects.all()
pprint(customers)
##c = customers[0]
#c.discount_percentage = 0.25
#c.save()

#customer = Customer(name='Henrik',
#                    customer_number=2,
#                    invoice_city='Helsingborg',
#                    invoice_postal_code='25269',
#                    is_private_person=False,
#                    is_active=True,
#                    )

#print(customer)
#inv = CustomerInvoiceDraft.objects.all()
#pprint(inv)
#inv = CustomerInvoiceDraft.objects.get('840d912b-16a0-4aaa-b113-1103a94a6d36')
#invoice.your_reference = 'UpdatedFromCli'
#invoice.save()
#print(invoice.created)
# invoice._delete()
# print(invoice)
# pprint(api.new_customer_invoice_draft(invoice))


#inv = CustomerInvoiceDraft(customer_id='34a10091-80f2-4f6f-abf8-3f426ae16600',
#                           customer_name='test_name',
#                           postal_code='25269',
#                           city='Helsingborg', customer_is_private_person=False)

#row = CustomerInvoiceDraftRow(line_number=1, article_id='b6934293-7f0d-41d5-906b-35ee410ae3b1', text='Test Artikel', unit_price=30.00, quantity=5)
#inv.rows.append(row)
#inv.save()

#print(inv.rows)
