# -*- coding: utf-8 -*-
# This file is part of the Smali Emulator.
#
# Copyright(c) 2016 Simone 'evilsocket' Margaritelli
# evilsocket@gmail.com
# http://www.evilsocket.net
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 3 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


class String:

    @staticmethod
    def name():
        return 'java.lang.String'

    @staticmethod
    def methods():
        return {
            'new-instance': String.new_instance,
            '<init>([B)V': String.init_from_byte_array,
            '<init>([C)V': String.init_from_char_array,
            'charAt(I)C': String.charat,
            'toCharArray()[C': String.tochararray,
            'intern()Ljava/lang/String;': String.repr_intern,
            'valueOf(Ljava/lang/Object;)Ljava/lang/String;': String.valueof,
            'replace(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Ljava/lang/String;': String.replace,
            'substring(II)Ljava/lang/String;': String.substring,
            'equals(Ljava/lang/Object;)Z': String.equals
        }

    @staticmethod
    def repr_intern(vm, this, args):
        return str(vm[this])

    @staticmethod
    def new_instance():
        return ""

    @staticmethod
    def init_from_byte_array(vm, this, args):
        chs = []
        print(args[0])
        print(vm[args[0]])
        for item in vm[args[0]]:
            chs.append(chr(item))
        vm[this] = "".join(chs)
        vm.result = vm[this]

    @staticmethod
    def init_from_char_array(vm, this, args):
        vm[this] = "".join(vm[args[0]])
        vm.result = vm[this]

    @staticmethod
    def charat(vm, this, args):
        idx = vm[args[0]]
        obj = vm[this]
        vm.result = obj[idx]

    @staticmethod
    def tochararray(vm, this, args):
        vm.result = list(vm[this])

    @staticmethod
    def valueof(vm, this, args):
        vm.result = vm[this]

    @staticmethod
    def substring(vm, this, args):
        start = vm[args[0]]
        end = vm[args[1]]
        vm.result = vm[this][start:end]

    @staticmethod
    def replace(vm, this, args):
        vm.result = vm[this].replace(vm[args[0]], vm[args[1]])
    
    @staticmethod
    def equals(vm, this, args):
        if len(args) != 2:
            vm.result = False
        else:
            vm.result = vm[args[0]] is vm[args[1]]