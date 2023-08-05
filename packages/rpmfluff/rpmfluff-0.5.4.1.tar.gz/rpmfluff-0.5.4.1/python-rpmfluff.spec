%global modname rpmfluff

Name:          python-%{modname}
Version:       0.5.4.1
Release:       1%{?dist}
Summary:       Lightweight way of building RPMs, and sabotaging them

License:       GPLv2+
URL:           https://pagure.io/rpmfluff
Source0:       https://pagure.io/releases/%{modname}/%{modname}-%{version}.tar.xz

BuildArch:     noarch

%global _description \
rpmfluff provides a python library for building RPM packages, and\
sabotaging them so they are broken in controlled ways.\
\
It is intended for use when validating package analysis tools such as RPM lint.\
It can also be used to construct test cases for package management software\
such as rpm and yum.

%description %{_description}

%package -n python2-%{modname}
Summary:        %{summary}
%{?python_provide:%python_provide python2-%{modname}}
BuildRequires:  python2-devel
BuildRequires:  rpm-python
Requires:       rpm-build
Requires:       createrepo_c

%description -n python2-%{modname} %{_description}

Python 2 version.

%package -n python3-%{modname}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{modname}}
BuildRequires:  python3-devel
BuildRequires:  rpm-python3
Requires:       rpm-build
Requires:       createrepo_c

%description -n python3-%{modname} %{_description}

Python 3 version.

%prep
%autosetup -n %{modname}-%{version}

%build
%py2_build
%py3_build

%install
%py2_install
%py3_install

%check
python2 %{modname}.py
python3 %{modname}.py

%files -n python2-%{modname}
%license LICENSE
%doc README.md
%{python2_sitelib}/%{modname}.py*
%{python2_sitelib}/%{modname}-*.egg-info

%files -n python3-%{modname}
%license LICENSE
%doc README.md
%{python3_sitelib}/%{modname}.py
%{python3_sitelib}/__pycache__/%{modname}.*
%{python3_sitelib}/%{modname}-*.egg-info

%changelog
* Tue Feb 13 2018 Jan Hutar <jhutar@redhat.com> - 0.5.4-1
- Fixes RHBZ#1544361

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jun 28 2017 Jan Hutar <jhutar@redhat.com> - 0.5.3-1
- Support mixing noarch and archful packages in a yum repo build by Dan Callaghan <dcallagh@redhat.com>

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 0.5.2-2
- Rebuild for Python 3.6

* Thu Sep 29 2016 Jan Hutar <jhutar@redhat.com> - 0.5.2-1
- Lots of fixes by Dan Callaghan <dcallagh@redhat.com>

* Fri Jul 22 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.5.1-1
- Fix Requires for createrepo_c in py3 subpkg
- Fix crash on python2 due to non-existing shutil.which()

* Fri Jul 22 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.5-1
- Make package following guidelines
- Replace usage of obsolete createrepo_c with createrepo

* Thu Aug 20 2015 Jan Hutar <jhutar@redhat.com> - 0.4.2-1
- John Dulaney implemented weak dependencies

* Thu Jul 09 2015 Jan Hutar <jhutar@redhat.com> - 0.4-1
- David Shea did a lots of work to support Python 3
- RHEL5 (i.e. Python 2.4) support dropped

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 30 2014 Toshio Kuratomi <toshio@fedoraproject.org> - 0.3-13
- Replace pyhton-setuptools-devel BR with python-setuptools

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jul 30 2010 David Malcolm <dmalcolm@redhat.com> - 0.3-6
- rebuild for python 2.7

* Fri Feb 12 2010 Jan Hutar <jhutar@redhat.com> - 0.3-5
- Now version is in the separate file

* Tue Jan 26 2010 Jan Hutar <jhutar@redhat.com> - 0.3-4
- Fix for deprecated popen2 module

* Thu Jan 7 2010 Jan Hutar <jhutar@redhat.com> - 0.3-3
- Moved to use EGGs for distribution

* Mon Dec 21 2009 Jan Hutar <jhutar@redhat.com> - 0.3-2
- Added separate LICENSE file

* Fri Dec 18 2009 Jan Hutar <jhutar@redhat.com> - 0.3-1
- New version, first attempt to get to Fedora

* Tue Jul 08 2008 Jan Hutar <jhutar@redhat.com> - 0.1-1
- Initial version
- spec-file based on python-html2text.spec
