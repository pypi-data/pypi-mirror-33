# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Module of StyleSheetDeclaration interface.
"""


class StyleSheetDeclaration:
    """
    The StyleSheetDeclaration interface contains the methods for access the CSS
    declaration.
    """

    def get_value(self):
        """
        Returns the value of declaration.

        :return: The value of declaration.
        :rtype: str
        """

        pass

    def get_values(self):
        """
        Returns a list with the values of declaration.

        :return: The list with the values of declaration.
        :rtype: list(str)
        """

        pass

    def get_property(self):
        """
        Returns the property of declaration.

        :return: The property of declaration.
        :rtype: str
        """

        pass
