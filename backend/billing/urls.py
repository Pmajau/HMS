from django.urls import path
from . import views

urlpatterns = [
    path('',                                        views.InvoiceListCreateView.as_view(),  name='invoice_list'),
    path('<int:pk>/',                               views.InvoiceDetailView.as_view(),      name='invoice_detail'),
    path('patient/<int:patient_id>/',               views.PatientInvoicesView.as_view(),    name='patient_invoices'),
    path('my-invoices/',                            views.PatientInvoicesView.as_view(),    name='my_invoices'),
    path('<int:invoice_id>/items/',                 views.AddInvoiceItemView.as_view(),     name='invoice_items'),
    path('<int:invoice_id>/payments/',              views.RecordPaymentView.as_view(),      name='record_payment'),
    path('summary/',                                views.FinancialSummaryView.as_view(),   name='financial_summary'),
]