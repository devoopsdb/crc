import math

from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView

from .forms import *
from .models import *


class CableCalView(FormView):
    template_name = "app/cable_cal.html"
    form_class = CableCalForm

    def get_success_url(self):
        pk = self.object.pk
        return reverse("cable_detail", kwargs={"pk": pk})

    def form_valid(self, form):
        model = form.save(commit=False)
        transport = get_object_or_404(TransportList, pk=model.transport.pk)
        # transport.height

        all_reels = ReelsList.objects.values_list(
            "name",
            "height",
            "width",
            "diameter",
            "diameter_neck",
            "length_neck",
            "reel_type",
            "mass",
            "max_load",
        )
        if all_reels:
            (
                r_names,
                r_heights,
                r_widths,
                r_diameters,
                r_diameter_necks,
                r_length_necks,
                r_reel_types,
                r_masses,
                r_max_loads,
            ) = zip(*all_reels)
        else:
            (
                r_names,
                r_heights,
                r_widths,
                r_diameters,
                r_diameter_necks,
                r_length_necks,
                r_reel_types,
                r_masses,
                r_max_loads,
            ) = ([], [], [], [], [], [], [], [], [])

        order_num = form.cleaned_data["order_num"]
        transport = form.cleaned_data["transport"]

        cods = self.request.POST.getlist("cod")
        names = self.request.POST.getlist("name")
        order_lens = self.request.POST.getlist("order_len")
        masses = self.request.POST.getlist("mass")
        diameters = self.request.POST.getlist("diameter")
        con_nums = self.request.POST.getlist("con_num")
        max_lens = self.request.POST.getlist("max_len")

        L_values = []

        for c in range(len(diameters)):
            L_diameter = []
            for r in range(len(r_names)):
                L = (
                    math.pi
                    * r_length_necks[r]
                    * ((r_diameters[r] - 100) ** 2 - r_diameter_necks[r] ** 2)
                    * 0.93
                    / (4 * float(diameters[c]) ** 2 * 10**3)
                )
                L = round(L)
                L_diameter.append(L)

            L_values.append(L_diameter)

        print(L_values)
        print()

        cable_lens = []
        cable_lens_id = []

        for c in range(len(L_values)):
            max_len = max_lens[c]
            valid_lengths = [L for L in L_values[c] if L <= float(max_len)]
            if valid_lengths:
                max_valid_length = max(valid_lengths)
                cable_lens_id.append(L_values[c].index(max_valid_length))
                cable_lens.append(max(valid_lengths))
            else:
                cable_lens.append(1)

        r_names_select = []

        for r in cable_lens_id:
            r_names_select.append(r_names[r])

        reel_num = [round(float(a) / float(b)) for a, b in zip(order_lens, cable_lens)]
        reel_len = [round(float(a) / float(b)) for a, b in zip(order_lens, reel_num)]
        netto_1 = [round(float(a) * float(b)) for a, b in zip(reel_len, masses)]
        brutto_1 = [
            round(float(a) * float(b) + float(c))
            for a, b, c in zip(reel_len, masses, r_masses)
        ]
        netto_all = [round(float(a) * float(b)) for a, b in zip(order_lens, masses)]
        brutto_all = [
            round(float(a) * float(b) + float(c) * float(d))
            for a, b, c, d in zip(order_lens, masses, r_masses, reel_num)
        ]

        reel_num = [str(i) for i in reel_num]
        reel_len = [str(i) for i in reel_len]
        netto_1 = [str(i) for i in netto_1]
        brutto_1 = [str(i) for i in brutto_1]
        netto_all = [str(i) for i in netto_all]
        brutto_all = [str(i) for i in brutto_all]

        with transaction.atomic():
            cable_cal_instance = CableCal.objects.create(
                order_num=order_num,
                transport=transport,
                cod="\n".join(cods),
                name="\n".join(names),
                order_len="\n".join(order_lens),
                mass="\n".join(masses),
                diameter="\n".join(diameters),
                con_num="\n".join(con_nums),
                max_len="\n".join(max_lens),
                reel_name="\n".join(r_names_select),
                reel_num="\n".join(reel_num),
                reel_len="\n".join(reel_len),
                netto_1="\n".join(netto_1),
                brutto_1="\n".join(brutto_1),
                netto_all="\n".join(netto_all),
                brutto_all="\n".join(brutto_all),
            )

            self.object = cable_cal_instance

        return super().form_valid(form)


class CableCalList(ListView):
    model = CableCal
    template_name = "app/cable_cal_list.html"
    context_object_name = "cable_cal"


class CableCalDetail(DetailView):
    model = CableCal
    template_name = "app/cable_cal_detail.html"
    context_object_name = "cable_cal"


class CableCalDel(DeleteView):
    model = CableCal
    template_name = "app/cable_cal_del.html"
    success_url = reverse_lazy("cable_list")


class ReelsListView(ListView):
    model = ReelsList
    template_name = "app/reels.html"
    context_object_name = "reels"


class ReelsListDetail(DetailView):
    model = ReelsList
    template_name = "app/reels_detail.html"
    context_object_name = "reels"


class ReelsListCreate(CreateView):
    form_class = ReelsListForm
    template_name = "app/reels_add.html"
    success_url = reverse_lazy("reels_list")


class ReelsListDel(DeleteView):
    model = ReelsList
    template_name = "app/reels_del.html"
    success_url = reverse_lazy("reels_list")


class TransportListView(ListView):
    model = TransportList
    template_name = "app/transport.html"
    context_object_name = "transport"


class TransportListDetail(DetailView):
    model = TransportList
    template_name = "app/transport_detail.html"
    context_object_name = "transport"


class TransportListCreate(CreateView):
    form_class = TransportListForm
    template_name = "app/transport_add.html"
    success_url = reverse_lazy("transport_list")


class TransportListDel(DeleteView):
    model = TransportList
    template_name = "app/transport_del.html"
    success_url = reverse_lazy("transport_list")


def x(request):
    return render(request, "app/tessst.html")
